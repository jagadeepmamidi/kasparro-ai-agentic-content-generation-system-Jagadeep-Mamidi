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
    
    def generate_questions(self, product: ProductData) -> List[Question]:
        """Generate categorized questions from product data with strict count enforcement.
        
        Args:
            product: ProductData instance
            
        Returns:
            List of Question objects (minimum 15)
            
        Raises:
            ValueError: If unable to generate 15+ questions after retries
        """
        logger.info(f"Generating questions for product: {product.product_name}")
        
        questions = self._generate_questions_with_retry(product)
        logger.info(f"Successfully generated {len(questions)} questions")
        return questions
    
    def _generate_questions_with_retry(self, product: ProductData, max_attempts: int = 3) -> List[Question]:
        """Generate questions with retry logic for strict count enforcement.
        
        Args:
            product: ProductData instance
            max_attempts: Maximum number of attempts to get 15+ questions
            
        Returns:
            List of at least 15 Question objects
            
        Raises:
            ValueError: If unable to reach minimum count after all attempts
        """
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Question generation attempt {attempt}/{max_attempts}")
            questions = self._call_llm_for_questions(product)
            
            if len(questions) >= 15:
                return questions
            
            logger.warning(f"Attempt {attempt}: Got {len(questions)} questions, need 15+. Retrying...")
        
        # Failed after all attempts - fail loudly
        raise ValueError(
            f"Failed to generate minimum 15 questions after {max_attempts} attempts. "
            f"Last attempt produced only {len(questions)} questions. Cannot proceed."
        )
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=2, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError)),
        reraise=True
    )
    def _call_llm_for_questions(self, product: ProductData) -> List[Question]:
        """Make LLM call to generate questions with API retry logic.
        
        Args:
            product: ProductData instance
            
        Returns:
            List of Question objects (may be less than 15)
        """
        from src.prompts import get_question_generation_prompt, SYS_QUESTION_GENERATION
        from src.utils import parse_llm_json
        
        prompt = get_question_generation_prompt(product)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": SYS_QUESTION_GENERATION
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = parse_llm_json(response.choices[0].message.content)
            questions = []
            
            for q_data in result.get("questions", []):
                questions.append(Question(
                    question=q_data["question"],
                    category=q_data["category"]
                ))
            
            logger.info(f"LLM returned {len(questions)} questions")
            return questions
            
        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.error(f"OpenAI API error during question generation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate questions: {str(e)}")
            raise
