"""Integration tests for the complete pipeline with mocked LLM calls."""

import pytest
from unittest.mock import Mock, patch
import json
from pathlib import Path

from src.agents.langgraph_orchestrator import LangGraphOrchestrator
from src.schemas import ProductData


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "product_name": "Test Serum",
        "concentration": "10% Vitamin C",
        "skin_type": "Oily, Combination",
        "key_ingredients": "Vitamin C, Hyaluronic Acid",
        "benefits": "Brightening, Hydration",
        "how_to_use": "Apply daily",
        "side_effects": "None",
        "price": "₹699"
    }


@pytest.fixture
def mock_openai_responses():
    """Mock responses for all OpenAI calls in the pipeline."""
    return {
        "product_generation": json.dumps({
            "product_name": "Competitor Serum",
            "concentration": "5% Niacinamide",
            "skin_type": ["Dry", "Sensitive"],
            "key_ingredients": ["Niacinamide", "Ceramides"],
            "benefits": ["Hydration", "Barrier repair"],
            "usage_instructions": "Apply nightly",
            "side_effects": "Minimal",
            "price": "₹799"
        }),
        "question_generation": json.dumps({
            "questions": [
                {"question": f"Question {i}?", "category": ["Informational", "Safety", "Usage", "Purchase", "Comparison"][i % 5]}
                for i in range(15)
            ]
        }),
        "faq_answers": json.dumps({
            "qa_pairs": [
                {"question": f"Question {i}?", "answer": f"Answer {i}"}
                for i in range(15)
            ]
        }),
        "recommendation": "Both products are excellent choices for different skin types."
    }


class TestPipelineIntegration:
    """Integration tests for the complete pipeline."""
    
    @patch('src.agents.product_generator_agent.OpenAI')
    @patch('src.agents.question_generator_agent.OpenAI')
    @patch('src.agents.page_assembly_agent.OpenAI')
    def test_complete_pipeline_execution(
        self,
        mock_page_openai,
        mock_question_openai,
        mock_product_openai,
        sample_product_data,
        mock_openai_responses,
        tmp_path
    ):
        """Test end-to-end pipeline execution with mocked LLM calls."""
        # Setup mocks for ProductGeneratorAgent
        mock_product_client = Mock()
        mock_product_openai.return_value = mock_product_client
        mock_product_response = Mock()
        mock_product_response.choices = [Mock()]
        mock_product_response.choices[0].message.content = mock_openai_responses["product_generation"]
        mock_product_client.chat.completions.create.return_value = mock_product_response
        
        # Setup mocks for QuestionGeneratorAgent
        mock_question_client = Mock()
        mock_question_openai.return_value = mock_question_client
        mock_question_response = Mock()
        mock_question_response.choices = [Mock()]
        mock_question_response.choices[0].message.content = mock_openai_responses["question_generation"]
        mock_question_client.chat.completions.create.return_value = mock_question_response
        
        # Setup mocks for PageAssemblyAgent
        mock_page_client = Mock()
        mock_page_openai.return_value = mock_page_client
        
        # Mock for FAQ answers
        mock_faq_response = Mock()
        mock_faq_response.choices = [Mock()]
        mock_faq_response.choices[0].message.content = mock_openai_responses["faq_answers"]
        
        # Mock for recommendation
        mock_rec_response = Mock()
        mock_rec_response.choices = [Mock()]
        mock_rec_response.choices[0].message.content = mock_openai_responses["recommendation"]
        
        # Configure mock to return different responses for different calls
        mock_page_client.chat.completions.create.side_effect = [
            mock_faq_response,
            mock_rec_response
        ]
        
        # Execute pipeline
        orchestrator = LangGraphOrchestrator()
        output_files = orchestrator.run_pipeline(sample_product_data)
        
        # Assertions
        assert "faq" in output_files
        assert "product" in output_files
        assert "comparison" in output_files
        
        # Verify all output files exist
        for page_type, filepath in output_files.items():
            assert Path(filepath).exists()
            assert Path(filepath).stat().st_size > 0
        
        # Verify LLM calls were made
        assert mock_product_client.chat.completions.create.called
        assert mock_question_client.chat.completions.create.called
        assert mock_page_client.chat.completions.create.called
    
    @patch('src.agents.product_generator_agent.OpenAI')
    @patch('src.agents.question_generator_agent.OpenAI')
    @patch('src.agents.page_assembly_agent.OpenAI')
    def test_pipeline_output_structure(
        self,
        mock_page_openai,
        mock_question_openai,
        mock_product_openai,
        sample_product_data,
        mock_openai_responses
    ):
        """Test that pipeline outputs have correct structure."""
        # Setup mocks (same as above)
        mock_product_client = Mock()
        mock_product_openai.return_value = mock_product_client
        mock_product_response = Mock()
        mock_product_response.choices = [Mock()]
        mock_product_response.choices[0].message.content = mock_openai_responses["product_generation"]
        mock_product_client.chat.completions.create.return_value = mock_product_response
        
        mock_question_client = Mock()
        mock_question_openai.return_value = mock_question_client
        mock_question_response = Mock()
        mock_question_response.choices = [Mock()]
        mock_question_response.choices[0].message.content = mock_openai_responses["question_generation"]
        mock_question_client.chat.completions.create.return_value = mock_question_response
        
        mock_page_client = Mock()
        mock_page_openai.return_value = mock_page_client
        mock_faq_response = Mock()
        mock_faq_response.choices = [Mock()]
        mock_faq_response.choices[0].message.content = mock_openai_responses["faq_answers"]
        mock_rec_response = Mock()
        mock_rec_response.choices = [Mock()]
        mock_rec_response.choices[0].message.content = mock_openai_responses["recommendation"]
        mock_page_client.chat.completions.create.side_effect = [mock_faq_response, mock_rec_response]
        
        # Execute
        orchestrator = LangGraphOrchestrator()
        output_files = orchestrator.run_pipeline(sample_product_data)
        
        # Load and verify FAQ structure
        import json
        with open(output_files["faq"], 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        
        assert faq_data["page_type"] == "faq"
        assert "product_name" in faq_data
        assert "faq_items" in faq_data
        assert "total_questions" in faq_data
        assert len(faq_data["faq_items"]) == faq_data["total_questions"]
        
        # Load and verify product page structure
        with open(output_files["product"], 'r', encoding='utf-8') as f:
            product_data = json.load(f)
        
        assert product_data["page_type"] == "product"
        assert "sections" in product_data
        
        # Load and verify comparison page structure
        with open(output_files["comparison"], 'r', encoding='utf-8') as f:
            comparison_data = json.load(f)
        
        assert comparison_data["page_type"] == "comparison"
        assert "products" in comparison_data
        assert "comparisons" in comparison_data
        assert "recommendation" in comparison_data
