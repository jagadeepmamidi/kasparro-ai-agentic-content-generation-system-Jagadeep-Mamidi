"""Product page template definition."""

from typing import Dict, Any


class ProductTemplate:
    """Template for product page structure."""
    
    @staticmethod
    def get_structure() -> Dict[str, Any]:
        """Get product page template structure.
        
        Returns:
            Template structure definition
        """
        return {
            "page_type": "product",
            "required_fields": [
                "product_name",
                "sections"
            ],
            "sections": {
                "overview": {
                    "fields": ["product_name", "concentration", "price"],
                    "dependencies": ["product_data"]
                },
                "benefits": {
                    "fields": ["title", "items", "description"],
                    "dependencies": ["benefits_block"]
                },
                "ingredients": {
                    "fields": ["title", "ingredients", "concentration"],
                    "dependencies": ["ingredients_block"]
                },
                "usage": {
                    "fields": ["title", "instructions", "tips"],
                    "dependencies": ["usage_block"]
                },
                "safety": {
                    "fields": ["title", "side_effects", "precautions"],
                    "dependencies": ["safety_block"]
                },
                "skin_type": {
                    "fields": ["title", "skin_types", "description"],
                    "dependencies": ["skin_type_block"]
                }
            }
        }
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> bool:
        """Validate product page data against template.
        
        Args:
            data: Page data to validate
            
        Returns:
            True if valid
        """
        if data.get("page_type") != "product":
            return False
        
        if "product_name" not in data or "sections" not in data:
            return False
        
        required_sections = ["overview", "benefits", "ingredients", "usage", "safety", "skin_type"]
        sections = data.get("sections", {})
        
        return all(section in sections for section in required_sections)
