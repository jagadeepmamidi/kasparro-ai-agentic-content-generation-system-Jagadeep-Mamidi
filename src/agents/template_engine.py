"""Template Engine - Manages templates and field mappings."""

from typing import Dict, Any
from src.templates import FAQTemplate, ProductTemplate, ComparisonTemplate
from src.utils import setup_logging

logger = setup_logging(__name__)


class TemplateEngine:
    """Agent responsible for managing templates.
    
    Input: Template name, data context
    Output: Template structure with field specifications
    Responsibility: Provide template definitions and validate data against templates
    """
    
    def __init__(self):
        """Initialize the Template Engine."""
        self.templates = {
            "faq": FAQTemplate,
            "product": ProductTemplate,
            "comparison": ComparisonTemplate
        }
        logger.info(f"TemplateEngine initialized with {len(self.templates)} templates")
    
    def get_template(self, template_name: str) -> Dict[str, Any]:
        """Get template structure.
        
        Args:
            template_name: Name of the template (faq, product, comparison)
            
        Returns:
            Template structure definition
            
        Raises:
            ValueError: If template name is not found
        """
        logger.info(f"Retrieving template: {template_name}")
        
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template_class = self.templates[template_name]
        return template_class.get_structure()
    
    def validate_data(self, template_name: str, data: Dict[str, Any]) -> bool:
        """Validate data against template.
        
        Args:
            template_name: Name of the template
            data: Data to validate
            
        Returns:
            True if data is valid for template
            
        Raises:
            ValueError: If template name is not found
        """
        logger.info(f"Validating data against template: {template_name}")
        
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template_class = self.templates[template_name]
        is_valid = template_class.validate(data)
        
        if is_valid:
            logger.info(f"Data is valid for template: {template_name}")
        else:
            logger.warning(f"Data validation failed for template: {template_name}")
        
        return is_valid
    
    def list_available_templates(self) -> list[str]:
        """Get list of available templates.
        
        Returns:
            List of template names
        """
        return list(self.templates.keys())
