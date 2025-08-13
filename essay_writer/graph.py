from typing import Dict, Any, List

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage

from .schema import AgentState, Queries

def build_graph(model, tavily_client, use_research_flag: bool, prompts: Dict[str, str]):
    """
    Build and compile the LangGraph pipeline.

    prompts: dict with keys ["plan", "writer", "reflection", "research_plan", "research_critique"]
    """
    memory = MemorySaver()

    PLAN_PROMPT = prompts["plan"]
    WRITER_PROMPT = prompts["writer"]
    REFLECTION_PROMPT = prompts["reflection"]
    RESEARCH_PLAN_PROMPT = prompts["research_plan"]
    RESEARCH_CRITIQUE_PROMPT = prompts["research_critique"]

    def plan_node(state: AgentState):
        messages = [SystemMessage(content=PLAN_PROMPT), HumanMessage(content=state["task"])]
        response = model.invoke(messages)
        return {"plan": response.content}

    def research_plan_node(state: AgentState):
        if not (use_research_flag and tavily_client):
            return {}
        queries = model.with_structured_output(Queries).invoke(
            [SystemMessage(content=RESEARCH_PLAN_PROMPT), HumanMessage(content=state["task"])]
        )
        content: List[str] = list(state.get("content", []))
        for q in queries.queries:
            try:
                resp = tavily_client.search(query=q, max_results=2)
                for r in resp.get("results", []):
                    if r.get("content"):
                        content.append(r["content"])
            except Exception as e:
                content.append(f"[Research error for '{q}': {e}]")
        return {"content": content}

    def generation_node(state: AgentState):
        content_blob = "\n\n".join(state.get("content", []))
        user_message = HumanMessage(content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}")
        messages = [SystemMessage(content=WRITER_PROMPT.format(content=content_blob)), user_message]
        response = model.invoke(messages)
        return {"draft": response.content, "revision_number": state.get("revision_number", 1) + 1}

    def reflection_node(state: AgentState):
        messages = [SystemMessage(content=REFLECTION_PROMPT), HumanMessage(content=state["draft"])]
        response = model.invoke(messages)
        return {"critique": response.content}

    def research_critique_node(state: AgentState):
        if not (use_research_flag and tavily_client):
            return {}
        queries = model.with_structured_output(Queries).invoke(
            [SystemMessage(content=RESEARCH_CRITIQUE_PROMPT), HumanMessage(content=state["critique"])]
        )
        content: List[str] = list(state.get("content", []))
        for q in queries.queries:
            try:
                resp = tavily_client.search(query=q, max_results=2)
                for r in resp.get("results", []):
                    if r.get("content"):
                        content.append(r["content"])
            except Exception as e:
                content.append(f"[Research error for '{q}': {e}]")
        return {"content": content}

    def should_continue(state: AgentState):
        if state["revision_number"] > state["max_revisions"]:
            return END
        return "reflect"

    builder = StateGraph(AgentState)
    builder.add_node("planner", plan_node)
    builder.add_node("research_plan", research_plan_node)
    builder.add_node("generate", generation_node)
    builder.add_node("reflect", reflection_node)
    builder.add_node("research_critique", research_critique_node)

    builder.set_entry_point("planner")
    builder.add_edge("planner", "research_plan")
    builder.add_edge("research_plan", "generate")
    builder.add_conditional_edges("generate", should_continue, {END: END, "reflect": "reflect"})
    builder.add_edge("reflect", "research_critique")
    builder.add_edge("research_critique", "generate")

    return builder.compile(checkpointer=memory)