from typing import List, TypedDict

# Prefer LC's vendored pydantic for compatibility; fallback to pydantic if needed
try:
    from langchain_core.pydantic_v1 import BaseModel
except Exception:
    from pydantic import BaseModel  # type: ignore


class Queries(BaseModel):
    queries: List[str]


class AgentState(TypedDict, total=False):
    task: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    revision_number: int
    max_revisions: int
    use_research: bool