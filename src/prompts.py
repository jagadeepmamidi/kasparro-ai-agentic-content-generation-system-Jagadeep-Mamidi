"""Centralized repository for all LLM prompts used in the system.

Decouples prompt logic from agent implementation for better maintainability and versioning.
"""

from typing import List
from src.schemas import ProductData, Question
from src.config import QUESTION_CATEGORIES, MIN_QUESTIONS_PER_CATEGORY

# System Prompts
SYS_QUESTION_GENERATION = (
    "You are an expert at generating user questions about skincare products. "
    "Generate diverse, realistic questions that users would ask. You MUST generate at least 15 questions."
)

SYS_PRODUCT_GENERATION = (
    "You are an expert at creating realistic fictional skincare products. "
    "Generate a competitor product that is similar but distinct from the reference product."
)

SYS_FAQ_ANSWERING = (
    "You are a helpful skincare product expert. "
    "Answer questions based only on the provided product information."
)

SYS_RECOMMENDATION = (
    "You are a skincare expert providing product recommendations."
)


def get_question_generation_prompt(product: ProductData) -> str:
    """Generate prompt for producing categorized questions."""
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


def get_competitor_product_prompt(reference_product: ProductData) -> str:
    """Generate prompt for creating a fictional competitor product."""
    return f"""Generate a realistic fictional competitor skincare product based on the reference product below.

The competitor product should:
1. Have a DIFFERENT product name (creative and realistic)
2. Target DIFFERENT or overlapping skin types
3. Use DIFFERENT key ingredients (but in the same category - e.g., if reference uses Vitamin C, competitor might use Niacinamide)
4. Offer similar but distinct benefits
5. Have competitive pricing (within 20% of reference price)
6. Be a realistic product that could exist in the market

Reference Product:
- Name: {reference_product.product_name}
- Concentration: {reference_product.concentration}
- Skin Types: {', '.join(reference_product.skin_type)}
- Key Ingredients: {', '.join(reference_product.key_ingredients)}
- Benefits: {', '.join(reference_product.benefits)}
- Usage: {reference_product.usage_instructions}
- Side Effects: {reference_product.side_effects}
- Price: {reference_product.price}

Generate a competitor product in this EXACT JSON structure:
{{
  "product_name": "...",
  "concentration": "...",
  "skin_type": ["...", "..."],
  "key_ingredients": ["...", "...", "..."],
  "benefits": ["...", "...", "..."],
  "usage_instructions": "...",
  "side_effects": "...",
  "price": "₹..."
}}

IMPORTANT: Return ONLY valid JSON matching the structure above. Ensure all fields are present and properly formatted.
"""


def get_faq_answering_prompt(product: ProductData, questions: List[Question]) -> str:
    """Generate prompt for batched FAQ answering."""
    questions_text = "\n".join([f"{i+1}. {q.question}" for i, q in enumerate(questions)])
    
    return f"""Answer ALL of the following questions about the product based ONLY on the provided product information.
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

Questions:
{questions_text}

Provide answers in JSON format with this structure:
{{
  "qa_pairs": [
    {{
      "question": "Original question text",
      "answer": "Answer to the question (2-3 sentences)"
    }},
    ...
  ]
}}

Ensure you provide answers for ALL {len(questions)} questions."""


def get_recommendation_prompt(product_a: ProductData, product_b: ProductData) -> str:
    """Generate prompt for product comparison recommendation."""
    return f"""Compare these two skincare products and provide a brief recommendation (2-3 sentences) 
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
