"""Tests for content logic blocks."""

import pytest
from src.schemas import ProductData
from src.content_logic_blocks import (
    generate_benefits_block,
    generate_usage_block,
    generate_ingredients_block,
    compare_ingredients_block
)


@pytest.fixture
def sample_product():
    """Sample product for testing."""
    return ProductData(
        product_name="Test Serum",
        concentration="10% Vitamin C",
        skin_type=["Oily", "Combination"],
        key_ingredients=["Vitamin C", "Hyaluronic Acid"],
        benefits=["Brightening", "Hydration"],
        usage_instructions="Apply daily",
        side_effects="None",
        price="₹699"
    )


def test_benefits_block(sample_product):
    """Test benefits block generation."""
    block = generate_benefits_block(sample_product)
    
    assert block.block_type == "benefits"
    assert "title" in block.content
    assert "items" in block.content
    assert len(block.content["items"]) == 2


def test_usage_block(sample_product):
    """Test usage block generation."""
    block = generate_usage_block(sample_product)
    
    assert block.block_type == "usage"
    assert "instructions" in block.content
    assert block.content["instructions"] == "Apply daily"


def test_ingredients_block(sample_product):
    """Test ingredients block generation."""
    block = generate_ingredients_block(sample_product)
    
    assert block.block_type == "ingredients"
    assert "ingredients" in block.content
    assert len(block.content["ingredients"]) == 2


def test_compare_ingredients_block(sample_product):
    """Test ingredient comparison block."""
    product_b = ProductData(
        product_name="Other Serum",
        skin_type=["Dry"],
        key_ingredients=["Niacinamide", "Hyaluronic Acid"],
        benefits=["Hydration"],
        usage_instructions="Apply nightly",
        price="₹899"
    )
    
    block = compare_ingredients_block(sample_product, product_b)
    
    assert block.block_type == "ingredient_comparison"
    assert "common_ingredients" in block.content
    assert "Hyaluronic Acid" in block.content["common_ingredients"]
