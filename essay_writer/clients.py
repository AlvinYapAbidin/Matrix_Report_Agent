import os
from typing import Optional

from langchain_openai import ChatOpenAI

def get_openai_model(model_name: str, temperature: float = 0.0) -> ChatOpenAI:
    # Relies on OPENAI_API_KEY in env
    return ChatOpenAI(model=model_name, temperature=temperature)

def get_tavily_client(api_key: Optional[str]):
    if not api_key:
        return None
    try:
        from tavily import TavilyClient
        return TavilyClient(api_key=api_key)
    except Exception:
        return None