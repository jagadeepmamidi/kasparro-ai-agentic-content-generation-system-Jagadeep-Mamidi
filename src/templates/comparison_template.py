"""Comparison page template definition."""

from typing import Dict, Any


class ComparisonTemplate:
    """Template for comparison page structure."""
    
    @staticmethod
    def get_structure() -> Dict[str, Any]:
        """Get comparison page template structure.
        
        Returns:
            Template structure definition
        """
        return {
            "page_type": "comparison",
            "required_fields": [
                "products",
                "comparisons",
                "recommendation"
            ],
            "products": {
                "product_a": ["name", "ingredients", "benefits", "price", "skin_type"],
                "product_b": ["name", "ingredients", "benefits", "price", "skin_type"]
            },
            "comparisons": {
                "ingredients": {
                    "dependencies": ["compare_ingredients_block"]
                },
                "benefits": {
                    "dependencies": ["compare_benefits_block"]
                },
                "price": {
                    "dependencies": ["compare_price_block"]
                },
                "skin_types": {
                    "dependencies": ["product_data"]
                }
            }
        }
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> bool:
        """Validate comparison page data against template.
        
        Args:
            data: Page data to validate
            
        Returns:
            True if valid
        """
        if data.get("page_type") != "comparison":
            return False
        
        required = ["products", "comparisons"]
        if not all(field in data for field in required):
            return False
        
        products = data.get("products", {})
        if "product_a" not in products or "product_b" not in products:
            return False
        
        comparisons = data.get("comparisons", {})
        required_comparisons = ["ingredients", "benefits", "price", "skin_types"]
        
        return all(comp in comparisons for comp in required_comparisons)
