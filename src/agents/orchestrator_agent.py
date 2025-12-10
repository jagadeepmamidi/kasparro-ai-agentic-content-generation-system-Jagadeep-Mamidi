"""Orchestrator Agent - Coordinates the entire pipeline execution."""

from typing import Dict, Any
from pathlib import Path

from src.schemas import ProductData
from src.agents.data_parser_agent import DataParserAgent
from src.agents.question_generator_agent import QuestionGeneratorAgent
from src.agents.page_assembly_agent import PageAssemblyAgent
from src.utils import setup_logging, save_json
from src.config import OUTPUT_DIR

logger = setup_logging(__name__)


class OrchestratorAgent:
    """Agent responsible for coordinating the entire pipeline.
    
    Input: Raw product data
    Output: Three JSON files (faq.json, product_page.json, comparison_page.json)
    Responsibility: Execute agents in DAG order and manage data flow
    """
    
    def __init__(self):
        """Initialize the Orchestrator Agent."""
        self.data_parser = DataParserAgent()
        self.question_generator = QuestionGeneratorAgent()
        self.page_assembler = PageAssemblyAgent()
        logger.info("OrchestratorAgent initialized with all sub-agents")
    
    def run_pipeline(self, raw_product_data: Dict[str, Any], product_b_data: Dict[str, Any] = None) -> Dict[str, Path]:
        """Execute the complete content generation pipeline.
        
        This implements a DAG orchestration pattern:
        1. DataParserAgent → Parse raw data
        2. QuestionGeneratorAgent → Generate questions
        3. PageAssemblyAgent (FAQ) → Assemble FAQ page
        4. PageAssemblyAgent (Product) → Assemble product page
        5. PageAssemblyAgent (Comparison) → Assemble comparison page
        
        Args:
            raw_product_data: Raw product data dictionary
            product_b_data: Optional second product for comparison (fictional)
            
        Returns:
            Dictionary mapping page type to output file path
        """
        logger.info("=" * 60)
        logger.info("STARTING CONTENT GENERATION PIPELINE")
        logger.info("=" * 60)
        
        output_files = {}
        
        try:
            logger.info("\n[STEP 1/6] Parsing product data...")
            product_a = self.data_parser.parse(raw_product_data)
            logger.info(f"✓ Parsed: {product_a.product_name}")
            
            logger.info("\n[STEP 2/6] Parsing comparison product data...")
            if product_b_data is None:
                product_b_data = self._create_fictional_product_b()
            product_b = self.data_parser.parse(product_b_data)
            logger.info(f"✓ Parsed: {product_b.product_name}")
            
            logger.info("\n[STEP 3/6] Generating questions...")
            questions = self.question_generator.generate_questions(product_a)
            logger.info(f"✓ Generated {len(questions)} questions")
            self._log_question_distribution(questions)
            
            logger.info("\n[STEP 4/6] Assembling FAQ page...")
            faq_page = self.page_assembler.assemble_faq_page(product_a, questions)
            faq_path = OUTPUT_DIR / "faq.json"
            save_json(faq_page, faq_path)
            output_files["faq"] = faq_path
            logger.info(f"✓ FAQ page saved to {faq_path}")
            
            logger.info("\n[STEP 5/6] Assembling product page...")
            product_page = self.page_assembler.assemble_product_page(product_a)
            product_path = OUTPUT_DIR / "product_page.json"
            save_json(product_page, product_path)
            output_files["product"] = product_path
            logger.info(f"✓ Product page saved to {product_path}")
            
            logger.info("\n[STEP 6/6] Assembling comparison page...")
            comparison_page = self.page_assembler.assemble_comparison_page(product_a, product_b)
            comparison_path = OUTPUT_DIR / "comparison_page.json"
            save_json(comparison_page, comparison_path)
            output_files["comparison"] = comparison_path
            logger.info(f"✓ Comparison page saved to {comparison_path}")
            
            logger.info("\n" + "=" * 60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"\nGenerated {len(output_files)} pages:")
            for page_type, path in output_files.items():
                logger.info(f"  - {page_type}: {path}")
            
            return output_files
            
        except Exception as e:
            logger.error(f"\n❌ Pipeline failed: {str(e)}")
            raise
    
    def _create_fictional_product_b(self) -> Dict[str, Any]:
        """Create fictional Product B for comparison.
        
        Returns:
            Product B data dictionary
        """
        return {
            "product_name": "RadiantGlow Niacinamide Serum",
            "concentration": "5% Niacinamide",
            "skin_type": ["Dry", "Sensitive"],
            "key_ingredients": ["Niacinamide", "Ceramides", "Hyaluronic Acid"],
            "benefits": ["Hydration", "Strengthens skin barrier", "Reduces redness"],
            "usage_instructions": "Apply 3-4 drops in the evening after cleansing",
            "side_effects": "Generally well-tolerated, rare cases of mild irritation",
            "price": "₹899"
        }
    
    def _log_question_distribution(self, questions):
        """Log distribution of questions by category.
        
        Args:
            questions: List of Question objects
        """
        from collections import Counter
        
        categories = [q.category for q in questions]
        distribution = Counter(categories)
        
        logger.info("  Question distribution by category:")
        for category, count in sorted(distribution.items()):
            logger.info(f"    - {category}: {count}")
