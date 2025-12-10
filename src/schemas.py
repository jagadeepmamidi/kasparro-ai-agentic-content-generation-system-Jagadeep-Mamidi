"""Data schemas for the agentic content generation system using Pydantic."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ProductData(BaseModel):
    """Structured product data schema."""
    
    product_name: str = Field(..., description="Name of the product")
    concentration: Optional[str] = Field(None, description="Active ingredient concentration")
    skin_type: List[str] = Field(..., description="Compatible skin types")
    key_ingredients: List[str] = Field(..., description="List of key ingredients")
    benefits: List[str] = Field(..., description="Product benefits")
    usage_instructions: str = Field(..., description="How to use the product")
    side_effects: Optional[str] = Field(None, description="Potential side effects")
    price: str = Field(..., description="Product price")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "GlowBoost Vitamin C Serum",
                "concentration": "10% Vitamin C",
                "skin_type": ["Oily", "Combination"],
                "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
                "benefits": ["Brightening", "Fades dark spots"],
                "usage_instructions": "Apply 2–3 drops in the morning before sunscreen",
                "side_effects": "Mild tingling for sensitive skin",
                "price": "₹699"
            }
        }


class Question(BaseModel):
    """Question model with category."""
    
    question: str = Field(..., description="The question text")
    category: Literal["Informational", "Safety", "Usage", "Purchase", "Comparison"] = Field(
        ..., description="Question category"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the main benefits of GlowBoost Vitamin C Serum?",
                "category": "Informational"
            }
        }


class FAQItem(BaseModel):
    """FAQ question-answer pair."""
    
    question: str = Field(..., description="The question")
    answer: str = Field(..., description="The answer")
    category: str = Field(..., description="Question category")


class ContentBlock(BaseModel):
    """Reusable content block."""
    
    block_type: str = Field(..., description="Type of content block")
    content: dict = Field(..., description="Block content data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "block_type": "benefits",
                "content": {
                    "title": "Benefits",
                    "items": ["Brightening", "Fades dark spots"]
                }
            }
        }


class ProductPageContent(BaseModel):
    """Structured product page content."""
    
    page_type: Literal["product"] = "product"
    product_name: str
    sections: dict = Field(..., description="Page sections with content")


class ComparisonPageContent(BaseModel):
    """Structured comparison page content."""
    
    page_type: Literal["comparison"] = "comparison"
    products: dict = Field(..., description="Products being compared")
    comparisons: dict = Field(..., description="Comparison sections")
    recommendation: Optional[str] = Field(None, description="Recommendation based on comparison")


class FAQPageContent(BaseModel):
    """Structured FAQ page content."""
    
    page_type: Literal["faq"] = "faq"
    product_name: str
    faq_items: List[FAQItem]
    total_questions: int
