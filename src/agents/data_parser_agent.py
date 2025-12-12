"""Data Parser Agent - Converts raw product data into structured ProductData schema."""

from typing import Dict, Any, List, Union
from pydantic import ValidationError
from src.schemas import ProductData
from src.utils import setup_logging

logger = setup_logging(__name__)


class DataParserAgent:
    """Agent responsible for parsing and validating raw product data.
    
    Input: Raw dictionary with product fields
    Output: Validated ProductData instance
    Responsibility: Data validation, normalization, and structuring
    """
    
    def __init__(self):
        """Initialize the Data Parser Agent."""
        logger.info("DataParserAgent initialized")
    
    def _parse_list_field(self, value: Union[str, List[str]]) -> List[str]:
        """Parse a field that can be either a string or list into a list.
        
        Args:
            value: String (comma-separated) or list
            
        Returns:
            List of strings
        """
        if isinstance(value, str):
            return [item.strip() for item in value.split(',')]
        return value
    
    def parse(self, raw_data: Dict[str, Any]) -> ProductData:
        """Parse raw product data into structured schema.
        
        Args:
            raw_data: Dictionary containing product information
            
        Returns:
            Validated ProductData instance
            
        Raises:
            ValueError: If data validation fails
        """
        logger.info(f"Parsing product data: {raw_data.get('product_name', 'Unknown')}")
        
        try:
            # Normalize list fields
            if 'skin_type' in raw_data:
                raw_data['skin_type'] = self._parse_list_field(raw_data['skin_type'])
            
            if 'key_ingredients' in raw_data:
                raw_data['key_ingredients'] = self._parse_list_field(raw_data['key_ingredients'])
            
            if 'benefits' in raw_data:
                raw_data['benefits'] = self._parse_list_field(raw_data['benefits'])
            
            # Handle field name variations
            if 'how_to_use' in raw_data:
                raw_data['usage_instructions'] = raw_data.pop('how_to_use')
            
            product = ProductData(**raw_data)
            
            logger.info(f"Successfully parsed product: {product.product_name}")
            return product
            
        except ValidationError as e:
            logger.error(f"Pydantic validation failed: {e}")
            raise ValueError(f"Invalid product data - validation errors: {e}")
        except Exception as e:
            logger.error(f"Failed to parse product data: {str(e)}")
            raise ValueError(f"Invalid product data: {str(e)}")
