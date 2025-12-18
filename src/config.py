"""Configuration management for the agentic content generation system."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
DOCS_DIR = PROJECT_ROOT / "docs"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Fail-fast validation for API key (skip during testing when mocks are used)
import sys
_is_testing = (
    os.getenv("PYTEST_CURRENT_TEST") is not None or 
    "pytest" in sys.modules or
    os.getenv("TESTING") == "1"
)
if not OPENAI_API_KEY and not _is_testing:
    raise RuntimeError(
        "OPENAI_API_KEY environment variable is not set. "
        "Please set it in your .env file or environment before running the pipeline."
    )

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Configurable model with fallback

# Retry Configuration
MAX_RETRIES = 3
RETRY_BACKOFF_MULTIPLIER = 2  # Exponential backoff: 1s, 2s, 4s
RETRY_MIN_WAIT = 1  # Minimum wait time in seconds
RETRY_MAX_WAIT = 10  # Maximum wait time in seconds

# Question Generation Configuration
MIN_QUESTIONS_PER_CATEGORY = 3
QUESTION_CATEGORIES = [
    "Informational",
    "Safety",
    "Usage",
    "Purchase",
    "Comparison"
]

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
