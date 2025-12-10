"""Main entry point for the Kasparro AI Agentic Content Generation System.

This script demonstrates the multi-agent pipeline that generates structured
JSON content pages from product data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agents.orchestrator_agent import OrchestratorAgent
from src.utils import setup_logging

logger = setup_logging(__name__)


def main():
    """Run the content generation pipeline."""
    
    # GlowBoost Vitamin C Serum - The only factual input
    glowboost_data = {
        "product_name": "GlowBoost Vitamin C Serum",
        "concentration": "10% Vitamin C",
        "skin_type": "Oily, Combination",
        "key_ingredients": "Vitamin C, Hyaluronic Acid",
        "benefits": "Brightening, Fades dark spots",
        "how_to_use": "Apply 2–3 drops in the morning before sunscreen",
        "side_effects": "Mild tingling for sensitive skin",
        "price": "₹699"
    }
    
    logger.info("Initializing Kasparro AI Agentic Content Generation System")
    logger.info(f"Input Product: {glowboost_data['product_name']}")
    
    orchestrator = OrchestratorAgent()
    
    try:
        output_files = orchestrator.run_pipeline(glowboost_data)
        
        print("\n" + "=" * 60)
        print("SUCCESS! Content generation complete.")
        print("=" * 60)
        print("\nGenerated files:")
        for page_type, filepath in output_files.items():
            print(f"  ✓ {page_type.upper()}: {filepath}")
        print("\nYou can now review the JSON files in the output/ directory.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Pipeline execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
