# Kasparro AI Agentic Content Generation System - LangGraph Edition

A modular, multi-agent automation system that transforms structured product data into machine-readable JSON content pages through **LangGraph-orchestrated** agent workflows.

## Project Overview

This system demonstrates engineering-focused automation using a **LangGraph-based multi-agent architecture**. It takes a single product dataset as input and automatically generates three different content pages (FAQ, Product Description, Comparison) in structured JSON format.

**Key Features:**
- **LangGraph Framework** for graph-based workflow orchestration
- **Parallel Page Assembly** - FAQ, Product, and Comparison pages built concurrently
- 7 Specialized Agents with clear boundaries and responsibilities
- **LLM-Generated Competitor Products** (no hardcoded data)
- **Centralized Prompt Management** via `src/prompts.py`
- **Robust Q&A Matching** with fuzzy text alignment (handles LLM reordering)
- State Graph Orchestration with error handling and retry logic
- 8 Reusable Content Logic Blocks for modular content generation
- 3 Custom Templates (FAQ, Product, Comparison)
- Pydantic Schemas for data validation
- **Batched LLM Calls** for efficiency
- **Output Sanitization** - handles markdown fences in LLM responses
- **Fail-Fast Configuration** - errors immediately on missing API key
- Comprehensive Test Suite with mocked LLM responses
- Machine-Readable JSON Output

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Orchestrator (StateGraph)            │
│                  (Graph-based Coordination)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┐
       │               │               │              │
       ▼               ▼               ▼              ▼
┌──────────┐    ┌──────────┐    ┌──────────┐  ┌──────────┐
│  Data    │    │ Product  │    │ Question │  │   Page   │
│  Parser  │───▶│Generator │───▶│Generator │─▶│ Assembly │
│  Agent   │    │  Agent   │    │  Agent   │  │  Agent   │
└──────────┘    └──────────┘    └──────────┘  └─────┬────┘
                                                     │
                     ┌───────────────┼───────────────┐
                     │               │               │
                     ▼               ▼               ▼
             ┌──────────┐    ┌──────────┐    ┌──────────┐
             │ Content  │    │ Template │    │   LLM    │
             │  Logic   │    │  Engine  │    │(OpenAI)  │
             │  Engine  │    │          │    │+ Retry   │
             └──────────┘    └──────────┘    └──────────┘
```

## Project Structure

```
kasparro/
├── src/
│   ├── agents/
│   │   ├── data_parser_agent.py
│   │   ├── product_generator_agent.py      # LLM-based competitor generation
│   │   ├── question_generator_agent.py
│   │   ├── content_logic_engine.py
│   │   ├── template_engine.py
│   │   ├── page_assembly_agent.py
│   │   └── langgraph_orchestrator.py       # Parallel graph orchestration
│   ├── templates/
│   │   ├── faq_template.py
│   │   ├── product_template.py
│   │   └── comparison_template.py
│   ├── prompts.py                          # Centralized LLM prompts
│   ├── schemas.py
│   ├── content_logic_blocks.py
│   ├── config.py                           # Fail-fast API key validation
│   └── utils.py                            # Includes parse_llm_json helper
├── output/
│   ├── faq.json
│   ├── product_page.json
│   └── comparison_page.json
├── docs/
│   └── projectdocumentation.md
├── tests/
│   ├── test_schemas.py
│   ├── test_content_logic.py
│   ├── test_agents.py                      # NEW: Unit tests with mocked LLM
│   └── test_pipeline.py                    # NEW: Integration tests
├── main.py
└── requirements.txt
```

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- OpenAI API key

### Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd kasparro
   ```

2. Create virtual environment
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies (includes LangGraph, LangChain, Tenacity)
   ```bash
   pip install -r requirements.txt
   ```

4. Configure API key and environment variables
   ```bash
   # Copy example env file
   copy .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-...
   # OPENAI_MODEL=gpt-4o-mini  # Optional: override default model
   ```

## Running the Pipeline

### Basic Usage (Default Product)
```bash
python main.py
```

### Advanced Usage (Custom Product Data)
```bash
python main.py --product-file path/to/product.json
```

This will:
1. Parse the input product data (Product A)
2. **Generate a fictional competitor product (Product B) using LLM**
3. Generate 15+ categorized questions
4. Create FAQ page with batched Q&A generation
5. Create Product page with structured sections
6. Create Comparison page (Product A vs Product B)
7. Output three JSON files to `output/` directory

**Note**: Product B is now dynamically generated by an LLM agent based on Product A's characteristics, not hardcoded.

## Output Examples

### FAQ Page (output/faq.json)
```json
{
  "page_type": "faq",
  "product_name": "GlowBoost Vitamin C Serum",
  "faq_items": [
    {
      "question": "What are the main benefits?",
      "answer": "...",
      "category": "Informational"
    }
  ],
  "total_questions": 15
}
```

### Product Page (output/product_page.json)
```json
{
  "page_type": "product",
  "product_name": "GlowBoost Vitamin C Serum",
  "sections": {
    "overview": {...},
    "benefits": {...},
    "ingredients": {...},
    "usage": {...},
    "safety": {...},
    "skin_type": {...}
  }
}
```

### Comparison Page (output/comparison_page.json)
```json
{
  "page_type": "comparison",
  "products": {
    "product_a": {...},
    "product_b": {...}
  },
  "comparisons": {
    "ingredients": {...},
    "benefits": {...},
    "price": {...},
    "skin_types": {...}
  },
  "recommendation": "..."
}
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_schemas.py -v
pytest tests/test_agents.py -v        # Unit tests with mocked LLM
pytest tests/test_pipeline.py -v     # Integration tests
```

## Documentation

Comprehensive system documentation is available in `docs/projectdocumentation.md`, including:
- Problem statement
- Solution overview
- System design with diagrams
- Agent architecture
- Data flow
- Template specifications

## Key Design Principles

1. **Modularity**: Each agent has a single, well-defined responsibility
2. **Clear Boundaries**: Explicit input/output contracts for all agents
3. **Reusability**: Content logic blocks are pure functions
4. **Extensibility**: Easy to add new templates or content blocks
5. **Validation**: Pydantic schemas ensure data integrity
6. **Orchestration**: Parallel DAG pattern for automated workflow
7. **Fail-Fast**: No silent failures or fallback text - errors propagate immediately
8. **Centralized Prompts**: All LLM prompts in `src/prompts.py` for easy versioning

## Technology Stack

- **Python 3.10+**: Core language
- **LangGraph 0.2+**: Graph-based workflow orchestration
- **LangChain Core 0.3+**: Agent framework foundation
- **Pydantic 2.9+**: Data validation and schemas
- **OpenAI API**: LLM for content generation
- **Tenacity 8.2+**: Retry logic for LLM calls
- **pytest**: Testing framework with mocking support

## License

This project is created for the Kasparro AI assignment.


