# Kasparro AI Agentic Content Generation System

A modular, multi-agent automation system that transforms structured product data into machine-readable JSON content pages through orchestrated agent workflows.

## Project Overview

This system demonstrates engineering-focused automation using a multi-agent architecture. It takes a single product dataset as input and automatically generates three different content pages (FAQ, Product Description, Comparison) in structured JSON format.

**Key Features:**
- 6 Specialized Agents with clear boundaries and responsibilities
- DAG Orchestration for automated workflow execution
- 8 Reusable Content Logic Blocks for modular content generation
- 3 Custom Templates (FAQ, Product, Comparison)
- Pydantic Schemas for data validation
- Machine-Readable JSON Output

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OrchestratorAgent                        │
│                  (Pipeline Coordinator)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Data    │    │ Question │    │   Page   │
│  Parser  │───▶│Generator │───▶│ Assembly │
│  Agent   │    │  Agent   │    │  Agent   │
└──────────┘    └──────────┘    └─────┬────┘
                                      │
                      ┌───────────────┼───────────────┐
                      │               │               │
                      ▼               ▼               ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │ Content  │    │ Template │    │   LLM    │
              │  Logic   │    │  Engine  │    │(OpenAI)  │
              │  Engine  │    │          │    │          │
              └──────────┘    └──────────┘    └──────────┘
```

## Project Structure

```
kasparro/
├── src/
│   ├── agents/
│   │   ├── data_parser_agent.py
│   │   ├── question_generator_agent.py
│   │   ├── content_logic_engine.py
│   │   ├── template_engine.py
│   │   ├── page_assembly_agent.py
│   │   └── orchestrator_agent.py
│   ├── templates/
│   │   ├── faq_template.py
│   │   ├── product_template.py
│   │   └── comparison_template.py
│   ├── schemas.py
│   ├── content_logic_blocks.py
│   ├── config.py
│   └── utils.py
├── output/
│   ├── faq.json
│   ├── product_page.json
│   └── comparison_page.json
├── docs/
│   └── projectdocumentation.md
├── tests/
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
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure API key
   ```bash
   # Copy example env file
   copy .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-...
   ```

## Running the Pipeline

```bash
python main.py
```

This will:
1. Parse the GlowBoost Vitamin C Serum data
2. Generate 15+ categorized questions
3. Create FAQ page with Q&A pairs
4. Create Product page with structured sections
5. Create Comparison page (GlowBoost vs RadiantGlow)
6. Output three JSON files to `output/` directory

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

# Run specific test
pytest tests/test_agents.py -v
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
6. **Orchestration**: DAG pattern for automated workflow

## Technology Stack

- **Python 3.10+**: Core language
- **Pydantic**: Data validation and schemas
- **OpenAI API**: LLM for question generation and answers
- **pytest**: Testing framework

