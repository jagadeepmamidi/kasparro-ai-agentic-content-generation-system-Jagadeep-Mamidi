"""Page Assembly Agent - Assembles final pages from templates and content blocks."""

from typing import Dict, Any, List
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.schemas import ProductData, Question, FAQItem
from src.agents.content_logic_engine import ContentLogicEngine
from src.agents.template_engine import TemplateEngine
from src.config import OPENAI_API_KEY, OPENAI_MODEL, MAX_RETRIES, RETRY_MIN_WAIT, RETRY_MAX_WAIT
from src.utils import setup_logging

logger = setup_logging(__name__)


class PageAssemblyAgent:
    """Agent responsible for assembling complete pages.
    
    Input: Template name, ProductData, questions, additional context
    Output: Structured page data (dict)
    Responsibility: Combine templates with content blocks to create final pages
    """
    
    def __init__(self):
        """Initialize the Page Assembly Agent."""
        self.content_engine = ContentLogicEngine()
        self.template_engine = TemplateEngine()
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        logger.info("PageAssemblyAgent initialized")
    
    def assemble_faq_page(self, product: ProductData, questions: List[Question]) -> Dict[str, Any]:
        """Assemble FAQ page with batched answer generation.
        
        Args:
            product: ProductData instance
            questions: List of Question objects
            
        Returns:
            FAQ page data dictionary
        """
        logger.info(f"Assembling FAQ page for {product.product_name}")
        
        # Batch generate all answers in a single LLM call for efficiency
        answers = self._generate_answers_batch(product, questions)
        
        faq_items = []
        for question, answer in zip(questions, answers):
            faq_items.append({
                "question": question.question,
                "answer": answer,
                "category": question.category
            })
        
        page_data = {
            "page_type": "faq",
            "product_name": product.product_name,
            "faq_items": faq_items,
            "total_questions": len(faq_items)
        }
        
        if not self.template_engine.validate_data("faq", page_data):
            raise ValueError("FAQ page data failed template validation - cannot proceed with invalid data")
        
        logger.info(f"Assembled FAQ page with {len(faq_items)} items")
        return page_data
    
    def assemble_product_page(self, product: ProductData) -> Dict[str, Any]:
        """Assemble product page.
        
        Args:
            product: ProductData instance
            
        Returns:
            Product page data dictionary
        """
        logger.info(f"Assembling product page for {product.product_name}")
        
        benefits_block = self.content_engine.execute_block("benefits", product)
        ingredients_block = self.content_engine.execute_block("ingredients", product)
        usage_block = self.content_engine.execute_block("usage", product)
        safety_block = self.content_engine.execute_block("safety", product)
        skin_type_block = self.content_engine.execute_block("skin_type", product)
        
        page_data = {
            "page_type": "product",
            "product_name": product.product_name,
            "sections": {
                "overview": {
                    "product_name": product.product_name,
                    "concentration": product.concentration,
                    "price": product.price,
                    "description": f"Premium skincare solution for {', '.join(product.skin_type)} skin types."
                },
                "benefits": benefits_block.content,
                "ingredients": ingredients_block.content,
                "usage": usage_block.content,
                "safety": safety_block.content,
                "skin_type": skin_type_block.content
            }
        }
        
        if not self.template_engine.validate_data("product", page_data):
            raise ValueError("Product page data failed template validation - cannot proceed with invalid data")
        
        logger.info("Assembled product page successfully")
        return page_data
    
    def assemble_comparison_page(self, product_a: ProductData, product_b: ProductData) -> Dict[str, Any]:
        """Assemble comparison page.
        
        Args:
            product_a: First product
            product_b: Second product (fictional)
            
        Returns:
            Comparison page data dictionary
        """
        logger.info(f"Assembling comparison page: {product_a.product_name} vs {product_b.product_name}")
        
        ingredients_comp = self.content_engine.execute_block(
            "compare_ingredients", 
            product_a, 
            product_b=product_b
        )
        benefits_comp = self.content_engine.execute_block(
            "compare_benefits", 
            product_a, 
            product_b=product_b
        )
        price_comp = self.content_engine.execute_block(
            "compare_price", 
            product_a, 
            product_b=product_b
        )
        
        recommendation = self._generate_recommendation(product_a, product_b)
        
        page_data = {
            "page_type": "comparison",
            "products": {
                "product_a": {
                    "name": product_a.product_name,
                    "ingredients": product_a.key_ingredients,
                    "benefits": product_a.benefits,
                    "price": product_a.price,
                    "skin_type": product_a.skin_type
                },
                "product_b": {
                    "name": product_b.product_name,
                    "ingredients": product_b.key_ingredients,
                    "benefits": product_b.benefits,
                    "price": product_b.price,
                    "skin_type": product_b.skin_type
                }
            },
            "comparisons": {
                "ingredients": ingredients_comp.content,
                "benefits": benefits_comp.content,
                "price": price_comp.content,
                "skin_types": {
                    "product_a": product_a.skin_type,
                    "product_b": product_b.skin_type,
                    "analysis": f"{product_a.product_name} suits {', '.join(product_a.skin_type)} skin, while {product_b.product_name} suits {', '.join(product_b.skin_type)} skin."
                }
            },
            "recommendation": recommendation
        }
        
        if not self.template_engine.validate_data("comparison", page_data):
            raise ValueError("Comparison page data failed template validation - cannot proceed with invalid data")
        
        logger.info("Assembled comparison page successfully")
        return page_data
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=2, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError)),
        reraise=True
    )
    def _generate_answers_batch(self, product: ProductData, questions: List[Question]) -> List[str]:
        """Generate answers to multiple questions in a single batched LLM call.
        
        Uses robust matching to align answers with questions even if LLM reorders them.
        
        Args:
            product: ProductData instance
            questions: List of Question objects
            
        Returns:
            List of answer strings aligned with input questions
        """
        from src.prompts import get_faq_answering_prompt, SYS_FAQ_ANSWERING
        from src.utils import parse_llm_json
        
        prompt = get_faq_answering_prompt(product, questions)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYS_FAQ_ANSWERING},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            result = parse_llm_json(response.choices[0].message.content)
            qa_pairs = result.get("qa_pairs", [])
            
            # Map question text to answer for robust O(1) lookup
            # Normalize keys by stripping whitespace and lowering case for fuzzy-strict matching
            answer_map = {item["question"].strip().lower(): item["answer"] for item in qa_pairs}
            
            final_answers = []
            missing_questions = []
            
            for q in questions:
                # Try exact match first
                key = q.question.strip().lower()
                if key in answer_map:
                    final_answers.append(answer_map[key])
                else:
                    # Fallback: Try to find substring match if exact match fails
                    # This helps if LLM slightly altered the question text
                    match_found = False
                    for k, v in answer_map.items():
                        if k in key or key in k: # loose substring match
                            final_answers.append(v)
                            match_found = True
                            break
                    
                    if not match_found:
                        missing_questions.append(q.question)
            
            # Strict validation: must get answers for all questions
            if missing_questions:
                raise ValueError(
                    f"LLM failed to answer {len(missing_questions)} questions. "
                    f"Missing: {missing_questions[:3]}..."
                )
            
            if len(final_answers) != len(questions):
                 raise ValueError(
                    f"Aligned answer count ({len(final_answers)}) does not match question count ({len(questions)})."
                )

            return final_answers
            
        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.error(f"OpenAI API error during FAQ generation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate batched answers: {str(e)}")
            raise  # Fail loudly - no fallback allowed
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=2, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError)),
        reraise=True
    )
    def _generate_recommendation(self, product_a: ProductData, product_b: ProductData) -> str:
        """Generate recommendation based on comparison with retry logic.
        
        Args:
            product_a: First product
            product_b: Second product
            
        Returns:
            Recommendation text
        """
        from src.prompts import get_recommendation_prompt, SYS_RECOMMENDATION
        
        prompt = get_recommendation_prompt(product_a, product_b)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYS_RECOMMENDATION},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.error(f"OpenAI API error during recommendation generation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate recommendation: {str(e)}")
            raise  # Fail loudly - no fallback allowed
