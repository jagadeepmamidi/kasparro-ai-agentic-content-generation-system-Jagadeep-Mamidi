"""LangGraph Orchestrator - Graph-based pipeline orchestration using LangGraph framework."""

from typing import Dict, Any, TypedDict, List
from pathlib import Path
from langgraph.graph import StateGraph, END
from pydantic import ValidationError

from src.schemas import ProductData, Question
from src.agents.data_parser_agent import DataParserAgent
from src.agents.product_generator_agent import ProductGeneratorAgent
from src.agents.question_generator_agent import QuestionGeneratorAgent
from src.agents.page_assembly_agent import PageAssemblyAgent
from src.utils import setup_logging, save_json
from src.config import OUTPUT_DIR

logger = setup_logging(__name__)


class PipelineState(TypedDict):
    """State object for the content generation pipeline."""
    raw_product_data: Dict[str, Any]
    product_a: ProductData | None
    product_b: ProductData | None
    questions: List[Question] | None
    faq_page: Dict[str, Any] | None
    product_page: Dict[str, Any] | None
    comparison_page: Dict[str, Any] | None
    output_files: Dict[str, Path]
    error: str | None


class LangGraphOrchestrator:
    """LangGraph-based orchestrator for content generation pipeline.
    
    Implements a state graph workflow with:
    - Dynamic task routing
    - Error handling and recovery
    - Conditional execution
    - State management across nodes
    """
    
    def __init__(self):
        """Initialize the LangGraph Orchestrator."""
        self.data_parser = DataParserAgent()
        self.product_generator = ProductGeneratorAgent()
        self.question_generator = QuestionGeneratorAgent()
        self.page_assembler = PageAssemblyAgent()
        
        # Build the state graph
        self.graph = self._build_graph()
        logger.info("LangGraphOrchestrator initialized with state graph")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph for pipeline execution.
        
        Returns:
            Compiled StateGraph instance
        """
        # Create state graph
        workflow = StateGraph(PipelineState)
        
        # Add nodes for each pipeline step
        workflow.add_node("parse_product_a", self._parse_product_a_node)
        workflow.add_node("generate_product_b", self._generate_product_b_node)
        workflow.add_node("generate_questions", self._generate_questions_node)
        workflow.add_node("assemble_faq", self._assemble_faq_node)
        workflow.add_node("assemble_product", self._assemble_product_node)
        workflow.add_node("assemble_comparison", self._assemble_comparison_node)
        workflow.add_node("save_outputs", self._save_outputs_node)
        
        # Define the workflow edges
        workflow.set_entry_point("parse_product_a")
        workflow.add_edge("parse_product_a", "generate_product_b")
        workflow.add_edge("generate_product_b", "generate_questions")
        workflow.add_edge("generate_questions", "assemble_faq")
        workflow.add_edge("assemble_faq", "assemble_product")
        workflow.add_edge("assemble_product", "assemble_comparison")
        workflow.add_edge("assemble_comparison", "save_outputs")
        workflow.add_edge("save_outputs", END)
        
        # Compile the graph
        return workflow.compile()
    
    def run_pipeline(self, raw_product_data: Dict[str, Any]) -> Dict[str, Path]:
        """Execute the content generation pipeline using LangGraph.
        
        Args:
            raw_product_data: Raw product data dictionary
            
        Returns:
            Dictionary mapping page type to output file path
            
        Raises:
            Exception: If pipeline execution fails
        """
        logger.info("=" * 60)
        logger.info("STARTING LANGGRAPH CONTENT GENERATION PIPELINE")
        logger.info("=" * 60)
        
        # Initialize state
        initial_state: PipelineState = {
            "raw_product_data": raw_product_data,
            "product_a": None,
            "product_b": None,
            "questions": None,
            "faq_page": None,
            "product_page": None,
            "comparison_page": None,
            "output_files": {},
            "error": None
        }
        
        try:
            # Execute the graph
            final_state = self.graph.invoke(initial_state)
            
            if final_state.get("error"):
                raise Exception(f"Pipeline failed: {final_state['error']}")
            
            logger.info("\n" + "=" * 60)
            logger.info("LANGGRAPH PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"\nGenerated {len(final_state['output_files'])} pages:")
            for page_type, path in final_state["output_files"].items():
                logger.info(f"  - {page_type}: {path}")
            
            return final_state["output_files"]
            
        except Exception as e:
            logger.error(f"\nLangGraph pipeline failed: {str(e)}")
            raise
    
    # ========== Graph Node Functions ==========
    
    def _parse_product_a_node(self, state: PipelineState) -> PipelineState:
        """Node: Parse Product A data.
        
        Args:
            state: Current pipeline state
            
        Returns:
            Updated pipeline state
        """
        logger.info("\n[NODE: parse_product_a] Parsing input product data...")
        
        try:
            product_a = self.data_parser.parse(state["raw_product_data"])
            logger.info(f"Parsed Product A: {product_a.product_name}")
            state["product_a"] = product_a
        except Exception as e:
            logger.error(f"Failed to parse Product A: {str(e)}")
            state["error"] = f"Product A parsing failed: {str(e)}"
        
        return state
    
    def _generate_product_b_node(self, state: PipelineState) -> PipelineState:
        """Node: Generate fictional Product B using LLM.
        
        Args:
            state: Current pipeline state
            
        Returns:
            Updated pipeline state
        """
        logger.info("\n[NODE: generate_product_b] Generating competitor product...")
        
        try:
            if state["product_a"] is None:
                raise ValueError("Product A not available for competitor generation")
            
            # Generate competitor product using LLM - returns ProductData instance
            product_b = self.product_generator.generate_product(state["product_a"])
            logger.info(f"Generated Product B: {product_b.product_name}")
            
            # Store directly as ProductData instance
            state["product_b"] = product_b
        except Exception as e:
            logger.error(f"Failed to generate Product B: {str(e)}")
            state["error"] = f"Product B generation failed: {str(e)}"
        
        return state
    
    def _parse_product_b_node(self, state: PipelineState) -> PipelineState:
        """Node: Parse generated Product B data.
        
        Args:
            state: Current pipeline state
            
        Returns:
            Updated pipeline state
        """
        logger.info("\n[NODE: parse_product_b] Validating generated product...")
        
        try:
            # Product B is already a ProductData instance from generator
            # Just validate it's present
            if "raw_product_b_data" in state:
                product_b = ProductData(**state["raw_product_b_data"])
                logger.info(f"Validated Product B: {product_b.product_name}")
                state["product_b"] = product_b
            else:
                raise ValueError("Product B data not available")
        except Exception as e:
            logger.error(f"Failed to validate Product B: {str(e)}")
            state["error"] = f"Product B validation failed: {str(e)}"
        
        return state
    
    def _generate_questions_node(self, state: PipelineState) -> PipelineState:
        """Node: Generate FAQ questions.
        
        Args:
            state: Current pipeline state
            
        Returns:
            Updated pipeline state
        """
        logger.info("\n[NODE: generate_questions] Generating FAQ questions...")
        
        try:
            if state["product_a"] is None:
                raise ValueError("Product A not available for question generation")
            
            questions = self.question_generator.generate_questions(state["product_a"])
            logger.info(f"Generated {len(questions)} questions")
            
            # Log distribution
            from collections import Counter
            categories = [q.category for q in questions]
            distribution = Counter(categories)
            logger.info("  Question distribution:")
            for category, count in sorted(distribution.items()):
                logger.info(f"    - {category}: {count}")
            
            state["questions"] = questions
        except Exception as e:
            logger.error(f"Failed to generate questions: {str(e)}")
            state["error"] = f"Question generation failed: {str(e)}"
        
        return state
    
    def _assemble_faq_node(self, state: PipelineState) -> PipelineState:
        """Node: Assemble FAQ page.
        
        Args:
            state: Current pipeline state
            
        Returns:
            Updated pipeline state
        """
        logger.info("\n[NODE: assemble_faq] Assembling FAQ page...")
        
        try:
            if state["product_a"] is None or state["questions"] is None:
                raise ValueError("Product A or questions not available")
            
            faq_page = self.page_assembler.assemble_faq_page(
                state["product_a"],
                state["questions"]
            )
            logger.info(f"Assembled FAQ page with {len(faq_page['faq_items'])} items")
            state["faq_page"] = faq_page
        except Exception as e:
            logger.error(f"Failed to assemble FAQ page: {str(e)}")
            state["error"] = f"FAQ assembly failed: {str(e)}"
        
        return state
    
    def _assemble_product_node(self, state: PipelineState) -> PipelineState:
        """Node: Assemble product page.
        
        Args:
            state: Current pipeline state
            
        Returns:
            Updated pipeline state
        """
        logger.info("\n[NODE: assemble_product] Assembling product page...")
        
        try:
            if state["product_a"] is None:
                raise ValueError("Product A not available")
            
            product_page = self.page_assembler.assemble_product_page(state["product_a"])
            logger.info("Assembled product page")
            state["product_page"] = product_page
        except Exception as e:
            logger.error(f"Failed to assemble product page: {str(e)}")
            state["error"] = f"Product page assembly failed: {str(e)}"
        
        return state
    
    def _assemble_comparison_node(self, state: PipelineState) -> PipelineState:
        """Node: Assemble comparison page.
        
        Args:
            state: Current pipeline state
            
        Returns:
            Updated pipeline state
        """
        logger.info("\n[NODE: assemble_comparison] Assembling comparison page...")
        
        try:
            if state["product_a"] is None or state["product_b"] is None:
                raise ValueError("Product A or Product B not available")
            
            comparison_page = self.page_assembler.assemble_comparison_page(
                state["product_a"],
                state["product_b"]
            )
            logger.info(f"Assembled comparison: {state['product_a'].product_name} vs {state['product_b'].product_name}")
            state["comparison_page"] = comparison_page
        except Exception as e:
            logger.error(f"Failed to assemble comparison page: {str(e)}")
            state["error"] = f"Comparison page assembly failed: {str(e)}"
        
        return state
    
    def _save_outputs_node(self, state: PipelineState) -> PipelineState:
        """Node: Save all output files.
        
        Args:
            state: Current pipeline state
            
        Returns:
            Updated pipeline state
        """
        logger.info("\n[NODE: save_outputs] Saving output files...")
        
        try:
            output_files = {}
            
            if state["faq_page"]:
                faq_path = OUTPUT_DIR / "faq.json"
                save_json(state["faq_page"], faq_path)
                output_files["faq"] = faq_path
                logger.info(f"Saved FAQ: {faq_path}")
            
            if state["product_page"]:
                product_path = OUTPUT_DIR / "product_page.json"
                save_json(state["product_page"], product_path)
                output_files["product"] = product_path
                logger.info(f"Saved Product Page: {product_path}")
            
            if state["comparison_page"]:
                comparison_path = OUTPUT_DIR / "comparison_page.json"
                save_json(state["comparison_page"], comparison_path)
                output_files["comparison"] = comparison_path
                logger.info(f"Saved Comparison Page: {comparison_path}")
            
            state["output_files"] = output_files
        except Exception as e:
            logger.error(f"Failed to save outputs: {str(e)}")
            state["error"] = f"Output saving failed: {str(e)}"
        
        return state
