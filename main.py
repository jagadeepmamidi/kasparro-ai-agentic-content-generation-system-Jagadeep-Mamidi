"""Main entry point for the Kasparro AI Agentic Content Generation System.

This script demonstrates the LangGraph-based multi-agent pipeline that generates
structured JSON content pages from product data.
"""

import sys
import argparse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agents.langgraph_orchestrator import LangGraphOrchestrator
from src.utils import configure_logging, get_logger

# Configure logging once at startup
configure_logging()
logger = get_logger(__name__)


def load_product_data(args) -> dict:
    """Load product data based on command-line arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Product data dictionary
    """
    # If product file is specified, load from file
    if args.product_file:
        logger.info(f"Loading product data from file: {args.product_file}")
        with open(args.product_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Otherwise, use default GlowBoost product
    return {
        "product_name": "GlowBoost Vitamin C Serum",
        "concentration": "10% Vitamin C",
        "skin_type": "Oily, Combination",
        "key_ingredients": "Vitamin C, Hyaluronic Acid",
        "benefits": "Brightening, Fades dark spots",
        "how_to_use": "Apply 2–3 drops in the morning before sunscreen",
        "side_effects": "Mild tingling for sensitive skin",
        "price": "₹699"
    }


def parse_arguments():
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Kasparro AI Agentic Content Generation System - LangGraph Edition"
    )
    parser.add_argument(
        "--product-file",
        type=str,
        help="Path to JSON file containing product data"
    )
    return parser.parse_args()


def main():
    """Run the LangGraph-based content generation pipeline."""
    
    args = parse_arguments()
    
    # Load product data
    product_data = load_product_data(args)
    
    logger.info("=" * 70)
    logger.info("Kasparro AI Agentic Content Generation System - LangGraph Edition")
    logger.info("=" * 70)
    logger.info(f"Input Product: {product_data['product_name']}")
    logger.info(f"Using LangGraph Framework for orchestration")
    
    # Initialize LangGraph orchestrator
    orchestrator = LangGraphOrchestrator()
    
    try:
        # Execute the pipeline
        output_files = orchestrator.run_pipeline(product_data)
        
        print("\n" + "=" * 70)
        print("SUCCESS! LangGraph pipeline completed successfully.")
        print("=" * 70)
        print("\nGenerated files:")
        for page_type, filepath in output_files.items():
            print(f"  {page_type.upper()}: {filepath}")
        print("\nYou can now review the JSON files in the output/ directory.")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        logger.exception("LangGraph pipeline execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

