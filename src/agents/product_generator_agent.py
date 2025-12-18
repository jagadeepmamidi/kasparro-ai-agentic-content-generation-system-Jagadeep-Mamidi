"""Product Generator Agent - Generates fictional competitor products using LLM."""

from typing import Dict, Any
import json
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.schemas import ProductData
from src.config import OPENAI_API_KEY, OPENAI_MODEL, MAX_RETRIES, RETRY_MIN_WAIT, RETRY_MAX_WAIT
from src.utils import setup_logging

logger = setup_logging(__name__)


class ProductGeneratorAgent:
    """Agent responsible for generating fictional competitor products.
    
    Input: ProductData instance (reference product)
    Output: ProductData instance (generated competitor)
    Responsibility: Use LLM to synthesize realistic competitor product
    """
    
    def __init__(self):
        """Initialize the Product Generator Agent."""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        logger.info("ProductGeneratorAgent initialized")
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=2, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError)),
        reraise=True
    )
    def generate_product(self, reference_product: ProductData) -> ProductData:
        """Generate a fictional competitor product based on reference product.
        
        Args:
            reference_product: Reference ProductData instance
            
        Returns:
            Generated ProductData instance for competitor
            
        Raises:
            ValueError: If product generation or validation fails
        """
        from src.prompts import get_competitor_product_prompt, SYS_PRODUCT_GENERATION
        from src.utils import parse_llm_json
        
        logger.info(f"Generating competitor product based on: {reference_product.product_name}")
        
        prompt = get_competitor_product_prompt(reference_product)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": SYS_PRODUCT_GENERATION
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,  # Higher temperature for more creative generation
                response_format={"type": "json_object"}
            )
            
            result = parse_llm_json(response.choices[0].message.content)
            
            # Validate and create ProductData instance
            try:
                competitor_product = ProductData(**result)
                logger.info(f"Generated competitor product: {competitor_product.product_name}")
                return competitor_product
            except ValidationError as e:
                logger.error(f"Generated product failed Pydantic validation: {e}")
                raise ValueError(f"Generated product data is invalid: {e}")
                
        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.error(f"OpenAI API error during product generation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate competitor product: {str(e)}")
            raise ValueError(f"Product generation failed: {str(e)}")
