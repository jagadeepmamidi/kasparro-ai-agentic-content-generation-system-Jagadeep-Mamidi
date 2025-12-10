"""Content Logic Engine - Executes content logic blocks."""

from typing import Dict, Any
from src.schemas import ProductData, ContentBlock
from src.content_logic_blocks import CONTENT_LOGIC_REGISTRY
from src.utils import setup_logging

logger = setup_logging(__name__)


class ContentLogicEngine:
    """Agent responsible for executing content logic blocks.
    
    Input: ProductData, block name, parameters
    Output: ContentBlock
    Responsibility: Invoke appropriate logic blocks and manage transformations
    """
    
    def __init__(self):
        """Initialize the Content Logic Engine."""
        self.registry = CONTENT_LOGIC_REGISTRY
        logger.info(f"ContentLogicEngine initialized with {len(self.registry)} blocks")
    
    def execute_block(self, block_name: str, product: ProductData, **kwargs) -> ContentBlock:
        """Execute a content logic block.
        
        Args:
            block_name: Name of the block to execute
            product: ProductData instance
            **kwargs: Additional parameters for the block
            
        Returns:
            ContentBlock with generated content
            
        Raises:
            ValueError: If block name is not found
        """
        logger.info(f"Executing content block: {block_name}")
        
        if block_name not in self.registry:
            raise ValueError(f"Unknown content block: {block_name}")
        
        block_func = self.registry[block_name]
        
        try:
            result = block_func(product, **kwargs)
            logger.info(f"Successfully executed block: {block_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to execute block {block_name}: {str(e)}")
            raise
    
    def list_available_blocks(self) -> list[str]:
        """Get list of available content blocks.
        
        Returns:
            List of block names
        """
        return list(self.registry.keys())
