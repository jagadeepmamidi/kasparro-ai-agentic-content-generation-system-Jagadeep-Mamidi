"""FAQ page template definition."""

from typing import Dict, Any, List


class FAQTemplate:
    """Template for FAQ page structure."""
    
    @staticmethod
    def get_structure() -> Dict[str, Any]:
        """Get FAQ template structure.
        
        Returns:
            Template structure definition
        """
        return {
            "page_type": "faq",
            "required_fields": [
                "product_name",
                "faq_items",
                "total_questions"
            ],
            "faq_item_fields": [
                "question",
                "answer",
                "category"
            ],
            "dependencies": {
                "questions": "QuestionGeneratorAgent",
                "answers": "LLM-generated based on product data"
            }
        }
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> bool:
        """Validate FAQ page data against template.
        
        Args:
            data: Page data to validate
            
        Returns:
            True if valid
        """
        required = ["page_type", "product_name", "faq_items", "total_questions"]
        if not all(field in data for field in required):
            return False
        
        if data["page_type"] != "faq":
            return False
        
        for item in data.get("faq_items", []):
            if not all(field in item for field in ["question", "answer", "category"]):
                return False
        
        return True
