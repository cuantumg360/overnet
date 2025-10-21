import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Coste estimado por 1k tokens (EUR aprox). Ajustable.
COSTS = {
    "openai:gpt-4o-mini": 0.5,
    "anthropic:claude-haiku": 0.4,
    "gemini:1.5-pro": 0.35,
}

# Timeouts en segundos
TIMEOUTS = {
    "openai": 20,
    "anthropic": 20,
    "gemini": 20,
}

MOCK_MODE = os.getenv("MOCK_MODE", "0") == "1" or not OPENAI_API_KEY
