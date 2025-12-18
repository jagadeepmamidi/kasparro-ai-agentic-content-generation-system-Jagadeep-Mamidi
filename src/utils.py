"""Utility functions for the agentic content generation system."""

import json
import logging
from pathlib import Path
from typing import Any, Dict

# Global flag to ensure logging is configured only once
_logging_configured = False


def configure_logging() -> None:
    """Configure logging for the entire application.
    
    Should be called once at application startup.
    """
    global _logging_configured
    
    if _logging_configured:
        return
    
    from src.config import LOG_LEVEL, LOG_FORMAT
    
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler()]
    )
    
    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.
    
    Args:
        name: Module name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Backward compatibility - deprecated, use get_logger instead
def setup_logging(name: str) -> logging.Logger:
    """Set up logging for a module (deprecated - use get_logger).
    
    Args:
        name: Name of the logger (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return get_logger(name)


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


def parse_llm_json(content: str) -> Dict[str, Any]:
    """Parse JSON from LLM output, handling markdown fences.
    
    Args:
        content: Raw LLM output string
        
    Returns:
        Parsed dictionary
        
    Raises:
        json.JSONDecodeError: If parsing fails
    """
    clean_content = content.strip()
    
    # Strip markdown code blocks if present
    if clean_content.startswith("```"):
        # Remove opening fence
        if clean_content.startswith("```json"):
            clean_content = clean_content[7:]
        else:
            clean_content = clean_content[3:]
            
        # Remove closing fence
        if clean_content.endswith("```"):
            clean_content = clean_content[:-3]
    
    return json.loads(clean_content.strip())



