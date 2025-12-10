"""Tests for data schemas."""

import pytest
from src.schemas import ProductData, Question, ContentBlock


def test_product_data_creation():
    """Test ProductData schema creation."""
    data = {
        "product_name": "Test Serum",
        "concentration": "10%",
        "skin_type": ["Oily", "Combination"],
        "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
        "benefits": ["Brightening", "Hydration"],
        "usage_instructions": "Apply daily",
        "side_effects": "None",
        "price": "₹699"
    }
    
    product = ProductData(**data)
    assert product.product_name == "Test Serum"
    assert len(product.skin_type) == 2
    assert len(product.key_ingredients) == 2


def test_question_creation():
    """Test Question schema creation."""
    question = Question(
        question="What are the benefits?",
        category="Informational"
    )
    
    assert question.question == "What are the benefits?"
    assert question.category == "Informational"


def test_content_block_creation():
    """Test ContentBlock schema creation."""
    block = ContentBlock(
        block_type="benefits",
        content={"title": "Benefits", "items": ["Brightening"]}
    )
    
    assert block.block_type == "benefits"
    assert "title" in block.content
