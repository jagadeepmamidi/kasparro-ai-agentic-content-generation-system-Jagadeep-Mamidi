"""Page Assembly Agent - Assembles final pages from templates and content blocks."""

from typing import Dict, Any, List
import json
from openai import OpenAI

from src.schemas import ProductData, Question, FAQItem
from src.agents.content_logic_engine import ContentLogicEngine
from src.agents.template_engine import TemplateEngine
from src.config import OPENAI_API_KEY, OPENAI_MODEL
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
        """Assemble FAQ page.
        
        Args:
            product: ProductData instance
            questions: List of Question objects
            
        Returns:
            FAQ page data dictionary
        """
        logger.info(f"Assembling FAQ page for {product.product_name}")
        
        faq_items = []
        for question in questions:
            answer = self._generate_answer(product, question.question)
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
            logger.warning("FAQ page data failed template validation")
        
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
            logger.warning("Product page data failed template validation")
        
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
            logger.warning("Comparison page data failed template validation")
        
        logger.info("Assembled comparison page successfully")
        return page_data
    
    def _generate_answer(self, product: ProductData, question: str) -> str:
        """Generate answer to a question using LLM.
        
        Args:
            product: ProductData instance
            question: Question text
            
        Returns:
            Answer text
        """
        prompt = f"""Answer this question about the product based ONLY on the provided product information.
Do not add any information not present in the product data.

Product Information:
- Name: {product.product_name}
- Concentration: {product.concentration}
- Skin Types: {', '.join(product.skin_type)}
- Key Ingredients: {', '.join(product.key_ingredients)}
- Benefits: {', '.join(product.benefits)}
- Usage: {product.usage_instructions}
- Side Effects: {product.side_effects}
- Price: {product.price}

Question: {question}

Provide a concise, helpful answer (2-3 sentences maximum)."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful skincare product expert. Answer questions based only on the provided product information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate answer: {str(e)}")
            return "Information not available."
    
    def _generate_recommendation(self, product_a: ProductData, product_b: ProductData) -> str:
        """Generate recommendation based on comparison.
        
        Args:
            product_a: First product
            product_b: Second product
            
        Returns:
            Recommendation text
        """
        prompt = f"""Compare these two skincare products and provide a brief recommendation (2-3 sentences) 
about which product might be better for different use cases or skin types.

Product A: {product_a.product_name}
- Ingredients: {', '.join(product_a.key_ingredients)}
- Benefits: {', '.join(product_a.benefits)}
- Skin Types: {', '.join(product_a.skin_type)}
- Price: {product_a.price}

Product B: {product_b.product_name}
- Ingredients: {', '.join(product_b.key_ingredients)}
- Benefits: {', '.join(product_b.benefits)}
- Skin Types: {', '.join(product_b.skin_type)}
- Price: {product_b.price}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a skincare expert providing product recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate recommendation: {str(e)}")
            return "Both products have their unique benefits. Choose based on your specific skin needs."
