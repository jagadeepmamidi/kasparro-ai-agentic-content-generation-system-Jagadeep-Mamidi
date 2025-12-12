"""Tests for LLM-dependent agents with mocked OpenAI responses."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from src.schemas import ProductData, Question
from src.agents.question_generator_agent import QuestionGeneratorAgent
from src.agents.page_assembly_agent import PageAssemblyAgent
from src.agents.product_generator_agent import ProductGeneratorAgent


@pytest.fixture
def sample_product():
    """Sample product for testing."""
    return ProductData(
        product_name="Test Serum",
        concentration="10% Vitamin C",
        skin_type=["Oily", "Combination"],
        key_ingredients=["Vitamin C", "Hyaluronic Acid"],
        benefits=["Brightening", "Hydration"],
        usage_instructions="Apply daily",
        side_effects="None",
        price="₹699"
    )


@pytest.fixture
def sample_questions():
    """Sample questions for testing."""
    return [
        Question(question="What are the benefits?", category="Informational"),
        Question(question="Is it safe for sensitive skin?", category="Safety"),
        Question(question="How often should I use it?", category="Usage")
    ]


class TestQuestionGeneratorAgent:
    """Tests for QuestionGeneratorAgent with mocked LLM calls."""
    
    @patch('src.agents.question_generator_agent.OpenAI')
    def test_generate_questions_success(self, mock_openai_class, sample_product):
        """Test successful question generation with mocked OpenAI response."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "questions": [
                {"question": "What are the main benefits?", "category": "Informational"},
                {"question": "Is it safe?", "category": "Safety"},
                {"question": "How to use?", "category": "Usage"},
                {"question": "Where to buy?", "category": "Purchase"},
                {"question": "How does it compare?", "category": "Comparison"},
                {"question": "What ingredients?", "category": "Informational"},
                {"question": "Any side effects?", "category": "Safety"},
                {"question": "Best time to apply?", "category": "Usage"},
                {"question": "What's the price?", "category": "Purchase"},
                {"question": "Better than others?", "category": "Comparison"},
                {"question": "Suitable for my skin?", "category": "Informational"},
                {"question": "Can I use daily?", "category": "Safety"},
                {"question": "Morning or night?", "category": "Usage"},
                {"question": "Is it worth it?", "category": "Purchase"},
                {"question": "Vs competitor?", "category": "Comparison"}
            ]
        })
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        agent = QuestionGeneratorAgent()
        questions = agent.generate_questions(sample_product)
        
        # Assertions
        assert len(questions) >= 15
        assert all(isinstance(q, Question) for q in questions)
        assert mock_client.chat.completions.create.called


class TestPageAssemblyAgent:
    """Tests for PageAssemblyAgent with mocked LLM calls."""
    
    @patch('src.agents.page_assembly_agent.OpenAI')
    def test_generate_answers_batch(self, mock_openai_class, sample_product, sample_questions):
        """Test batched FAQ answer generation with mocked OpenAI response."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "answers": [
                "The main benefits are brightening and hydration.",
                "It may cause mild tingling for sensitive skin.",
                "Apply daily in the morning before sunscreen."
            ]
        })
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        agent = PageAssemblyAgent()
        answers = agent._generate_answers_batch(sample_product, sample_questions)
        
        # Assertions
        assert len(answers) == len(sample_questions)
        assert all(isinstance(a, str) for a in answers)
        assert mock_client.chat.completions.create.called
    
    @patch('src.agents.page_assembly_agent.OpenAI')
    def test_assemble_faq_page(self, mock_openai_class, sample_product, sample_questions):
        """Test FAQ page assembly with mocked LLM response."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "answers": ["Answer 1", "Answer 2", "Answer 3"]
        })
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        agent = PageAssemblyAgent()
        faq_page = agent.assemble_faq_page(sample_product, sample_questions)
        
        # Assertions
        assert faq_page["page_type"] == "faq"
        assert faq_page["product_name"] == sample_product.product_name
        assert len(faq_page["faq_items"]) == len(sample_questions)
        assert faq_page["total_questions"] == len(sample_questions)


class TestProductGeneratorAgent:
    """Tests for ProductGeneratorAgent with mocked LLM calls."""
    
    @patch('src.agents.product_generator_agent.OpenAI')
    def test_generate_product(self, mock_openai_class, sample_product):
        """Test product generation with mocked OpenAI response."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "product_name": "RadiantGlow Niacinamide Serum",
            "concentration": "5% Niacinamide",
            "skin_type": ["Dry", "Sensitive"],
            "key_ingredients": ["Niacinamide", "Ceramides", "Hyaluronic Acid"],
            "benefits": ["Hydration", "Strengthens skin barrier", "Reduces redness"],
            "usage_instructions": "Apply 3-4 drops in the evening after cleansing",
            "side_effects": "Generally well-tolerated, rare cases of mild irritation",
            "price": "₹899"
        })
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        agent = ProductGeneratorAgent()
        generated_product = agent.generate_product(sample_product)
        
        # Assertions
        assert isinstance(generated_product, ProductData)
        assert generated_product.product_name != sample_product.product_name
        assert mock_client.chat.completions.create.called
