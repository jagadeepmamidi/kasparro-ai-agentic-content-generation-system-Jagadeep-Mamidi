"""Utility functions for the agentic content generation system."""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from src.config import LOG_LEVEL, LOG_FORMAT


def setup_logging(name: str) -> logging.Logger:
    """Set up logging for a module.
    
    Args:
        name: Name of the logger (typically __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
    
    return logger


def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """Save data as formatted JSON file.
    
    Args:
        data: Dictionary to save
        filepath: Path to output file
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: Path) -> Dict[str, Any]:
    """Load JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded dictionary
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_json_structure(data: Dict[str, Any], required_fields: list[str]) -> bool:
    """Validate that JSON has required fields.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if all required fields present
    """
    return all(field in data for field in required_fields)
