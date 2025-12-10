"""Data Parser Agent - Converts raw product data into structured ProductData schema."""

from typing import Dict, Any
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
            if isinstance(raw_data.get('skin_type'), str):
                raw_data['skin_type'] = [s.strip() for s in raw_data['skin_type'].split(',')]
            
            if isinstance(raw_data.get('key_ingredients'), str):
                raw_data['key_ingredients'] = [i.strip() for i in raw_data['key_ingredients'].split(',')]
            
            if isinstance(raw_data.get('benefits'), str):
                raw_data['benefits'] = [b.strip() for b in raw_data['benefits'].split(',')]
            
            if 'how_to_use' in raw_data:
                raw_data['usage_instructions'] = raw_data.pop('how_to_use')
            
            product = ProductData(**raw_data)
            
            logger.info(f"Successfully parsed product: {product.product_name}")
            return product
            
        except Exception as e:
            logger.error(f"Failed to parse product data: {str(e)}")
            raise ValueError(f"Invalid product data: {str(e)}")
