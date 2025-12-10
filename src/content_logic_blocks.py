"""Reusable content logic blocks for transforming product data into content."""

from typing import Dict, Any, List
from src.schemas import ProductData, ContentBlock


def generate_benefits_block(product: ProductData, **kwargs) -> ContentBlock:
    """Generate benefits content block.
    
    Args:
        product: Product data
        **kwargs: Additional parameters
        
    Returns:
        ContentBlock with benefits information
    """
    return ContentBlock(
        block_type="benefits",
        content={
            "title": "Key Benefits",
            "items": product.benefits,
            "description": f"{product.product_name} offers multiple benefits for your skin."
        }
    )


def generate_usage_block(product: ProductData, **kwargs) -> ContentBlock:
    """Generate usage instructions content block.
    
    Args:
        product: Product data
        **kwargs: Additional parameters
        
    Returns:
        ContentBlock with usage instructions
    """
    return ContentBlock(
        block_type="usage",
        content={
            "title": "How to Use",
            "instructions": product.usage_instructions,
            "tips": "For best results, use consistently as part of your skincare routine."
        }
    )


def generate_ingredients_block(product: ProductData, **kwargs) -> ContentBlock:
    """Generate ingredients content block.
    
    Args:
        product: Product data
        **kwargs: Additional parameters
        
    Returns:
        ContentBlock with ingredients information
    """
    return ContentBlock(
        block_type="ingredients",
        content={
            "title": "Key Ingredients",
            "ingredients": product.key_ingredients,
            "concentration": product.concentration if product.concentration else "Not specified"
        }
    )


def generate_safety_block(product: ProductData, **kwargs) -> ContentBlock:
    """Generate safety information content block.
    
    Args:
        product: Product data
        **kwargs: Additional parameters
        
    Returns:
        ContentBlock with safety information
    """
    return ContentBlock(
        block_type="safety",
        content={
            "title": "Safety Information",
            "side_effects": product.side_effects if product.side_effects else "No known side effects",
            "precautions": "Perform a patch test before first use. Discontinue if irritation occurs."
        }
    )


def generate_skin_type_block(product: ProductData, **kwargs) -> ContentBlock:
    """Generate skin type compatibility block.
    
    Args:
        product: Product data
        **kwargs: Additional parameters
        
    Returns:
        ContentBlock with skin type information
    """
    return ContentBlock(
        block_type="skin_type",
        content={
            "title": "Suitable For",
            "skin_types": product.skin_type,
            "description": f"Formulated for {', '.join(product.skin_type)} skin types."
        }
    )


def compare_ingredients_block(product_a: ProductData, product_b: ProductData, **kwargs) -> ContentBlock:
    """Compare ingredients between two products.
    
    Args:
        product_a: First product
        product_b: Second product
        **kwargs: Additional parameters
        
    Returns:
        ContentBlock with ingredient comparison
    """
    common = set(product_a.key_ingredients) & set(product_b.key_ingredients)
    unique_a = set(product_a.key_ingredients) - set(product_b.key_ingredients)
    unique_b = set(product_b.key_ingredients) - set(product_a.key_ingredients)
    
    return ContentBlock(
        block_type="ingredient_comparison",
        content={
            "title": "Ingredient Comparison",
            "product_a": {
                "name": product_a.product_name,
                "ingredients": product_a.key_ingredients,
                "unique": list(unique_a)
            },
            "product_b": {
                "name": product_b.product_name,
                "ingredients": product_b.key_ingredients,
                "unique": list(unique_b)
            },
            "common_ingredients": list(common)
        }
    )


def compare_benefits_block(product_a: ProductData, product_b: ProductData, **kwargs) -> ContentBlock:
    """Compare benefits between two products.
    
    Args:
        product_a: First product
        product_b: Second product
        **kwargs: Additional parameters
        
    Returns:
        ContentBlock with benefits comparison
    """
    common = set(product_a.benefits) & set(product_b.benefits)
    unique_a = set(product_a.benefits) - set(product_b.benefits)
    unique_b = set(product_b.benefits) - set(product_a.benefits)
    
    return ContentBlock(
        block_type="benefits_comparison",
        content={
            "title": "Benefits Comparison",
            "product_a": {
                "name": product_a.product_name,
                "benefits": product_a.benefits,
                "unique": list(unique_a)
            },
            "product_b": {
                "name": product_b.product_name,
                "benefits": product_b.benefits,
                "unique": list(unique_b)
            },
            "common_benefits": list(common)
        }
    )


def compare_price_block(product_a: ProductData, product_b: ProductData, **kwargs) -> ContentBlock:
    """Compare prices between two products.
    
    Args:
        product_a: First product
        product_b: Second product
        **kwargs: Additional parameters
        
    Returns:
        ContentBlock with price comparison
    """
    return ContentBlock(
        block_type="price_comparison",
        content={
            "title": "Price Comparison",
            "product_a": {
                "name": product_a.product_name,
                "price": product_a.price
            },
            "product_b": {
                "name": product_b.product_name,
                "price": product_b.price
            },
            "analysis": f"{product_a.product_name} is priced at {product_a.price} while {product_b.product_name} is priced at {product_b.price}."
        }
    )


CONTENT_LOGIC_REGISTRY = {
    "benefits": generate_benefits_block,
    "usage": generate_usage_block,
    "ingredients": generate_ingredients_block,
    "safety": generate_safety_block,
    "skin_type": generate_skin_type_block,
    "compare_ingredients": compare_ingredients_block,
    "compare_benefits": compare_benefits_block,
    "compare_price": compare_price_block,
}
