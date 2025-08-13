# essay_writer/__init__.py
"""
Essay Writer package: LangGraph builders, schemas, and prompts.
"""

__version__ = "0.1.0"

# Re-export common entry points for convenience:
from .schema import AgentState, Queries
from .graph import build_graph
from .clients import get_openai_model, get_tavily_client
from .prompts import (
    PLAN_PROMPT,
    WRITER_PROMPT,
    REFLECTION_PROMPT,
    RESEARCH_PLAN_PROMPT,
    RESEARCH_CRITIQUE_PROMPT,
)

__all__ = [
    "__version__",
    "AgentState",
    "Queries",
    "build_graph",
    "get_openai_model",
    "get_tavily_client",
    "PLAN_PROMPT",
    "WRITER_PROMPT",
    "REFLECTION_PROMPT",
    "RESEARCH_PLAN_PROMPT",
    "RESEARCH_CRITIQUE_PROMPT",
]