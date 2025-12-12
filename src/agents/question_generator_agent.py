"""Question Generator Agent - Generates categorized questions from product data."""

from typing import List
import json
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.schemas import ProductData, Question
from src.config import OPENAI_API_KEY, OPENAI_MODEL, QUESTION_CATEGORIES, MIN_QUESTIONS_PER_CATEGORY, MAX_RETRIES, RETRY_MIN_WAIT, RETRY_MAX_WAIT
from src.utils import setup_logging

logger = setup_logging(__name__)


class QuestionGeneratorAgent:
    """Agent responsible for generating categorized questions.
    
    Input: ProductData instance
    Output: List of Question objects (15+ questions across 5 categories)
    Responsibility: Generate diverse, relevant questions using LLM
    """
    
    def __init__(self):
        """Initialize the Question Generator Agent."""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        logger.info("QuestionGeneratorAgent initialized")
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=2, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError)),
        reraise=True
    )
    def generate_questions(self, product: ProductData) -> List[Question]:
        """Generate categorized questions from product data with retry logic.
        
        Args:
            product: ProductData instance
            
        Returns:
            List of Question objects (minimum 15)
        """
        logger.info(f"Generating questions for product: {product.product_name}")
        
        prompt = self._create_prompt(product)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at generating user questions about skincare products. Generate diverse, realistic questions that users would ask."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            questions = []
            
            for q_data in result.get("questions", []):
                questions.append(Question(
                    question=q_data["question"],
                    category=q_data["category"]
                ))
            
            logger.info(f"Generated {len(questions)} questions")
            
            if len(questions) < 15:
                logger.warning(f"Only generated {len(questions)} questions, expected 15+")
            
            return questions
            
        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.error(f"OpenAI API error during question generation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate questions: {str(e)}")
            raise
    
    def _create_prompt(self, product: ProductData) -> str:
        """Create prompt for question generation.
        
        Args:
            product: ProductData instance
            
        Returns:
            Formatted prompt string
        """
        return f"""Generate at least 15 diverse user questions about the following skincare product. 
Questions must be categorized into these categories: {', '.join(QUESTION_CATEGORIES)}.
Ensure at least {MIN_QUESTIONS_PER_CATEGORY} questions per category.

Product Information:
- Name: {product.product_name}
- Concentration: {product.concentration}
- Skin Types: {', '.join(product.skin_type)}
- Key Ingredients: {', '.join(product.key_ingredients)}
- Benefits: {', '.join(product.benefits)}
- Usage: {product.usage_instructions}
- Side Effects: {product.side_effects}
- Price: {product.price}

Return a JSON object with this structure:
{{
  "questions": [
    {{"question": "...", "category": "Informational"}},
    {{"question": "...", "category": "Safety"}},
    ...
  ]
}}

Categories must be one of: {', '.join(QUESTION_CATEGORIES)}
"""
