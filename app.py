import os
import uuid
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

from essay_writer.prompts import (
    PLAN_PROMPT,
    WRITER_PROMPT,
    REFLECTION_PROMPT,
    RESEARCH_PLAN_PROMPT,
    RESEARCH_CRITIQUE_PROMPT,
)
from essay_writer.schema import AgentState
from essay_writer.clients import get_openai_model, get_tavily_client
from essay_writer.graph import build_graph

# ----- UI Setup -----
st.set_page_config(page_title="Essay Writer (LangGraph)", page_icon="📝")
st.title("Essay Writer (LangGraph)")
st.caption("Outline → Research → Draft → Critique → Revise")

load_dotenv()

with st.sidebar:
    st.header("Settings")
    openai_key = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="Required",
    )
    tavily_key = st.text_input(
        "Tavily API Key (optional)",
        value=os.getenv("TAVILY_API_KEY", ""),
        type="password",
        help="Optional for web research",
    )

    model_name = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
    use_research = st.toggle("Use Tavily research", value=bool(tavily_key))
    max_revisions = st.number_input("Max revisions", 0, 5, 2, 1)

topic = st.text_area(
    "Your essay topic or question",
    placeholder="e.g., RAG-first beats Agents-first for most document workflows. Change my mind",
    height=120,
)

col1, col2 = st.columns([1, 1])
run_btn = col1.button("Write Essay", type="primary")
clear_btn = col2.button("Clear Output")

if clear_btn:
    for k in ("last_plan", "last_draft", "last_critique"):
        st.session_state.pop(k, None)
    st.rerun()

output_area = st.container()

# ----- Run -----
if run_btn:
    if not openai_key:
        st.error("Please provide an OpenAI API key.")
        st.stop()

    # Pass keys to underlying SDKs that read from env
    os.environ["OPENAI_API_KEY"] = openai_key
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key

    model = get_openai_model(model_name=model_name, temperature=temperature)
    tavily_client = get_tavily_client(tavily_key) if (use_research and tavily_key) else None

    graph = build_graph(
        model=model,
        tavily_client=tavily_client,
        use_research_flag=bool(tavily_client),
        prompts={
            "plan": PLAN_PROMPT,
            "writer": WRITER_PROMPT,
            "reflection": REFLECTION_PROMPT,
            "research_plan": RESEARCH_PLAN_PROMPT,
            "research_critique": RESEARCH_CRITIQUE_PROMPT,
        },
    )

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    init_state: AgentState = {
        "task": (topic or "").strip(),
        "max_revisions": int(max_revisions),
        "revision_number": 1,
        "content": [],
        "use_research": bool(tavily_client),
    }

    last_draft = ""
    with st.status("Working…", expanded=True) as status:
        st.write("Starting pipeline…")
        try:
            for update in graph.stream(init_state, config):
                if not isinstance(update, dict):
                    continue

                if "planner" in update:
                    plan = update["planner"].get("plan", "")
                    st.session_state["last_plan"] = plan
                    with output_area:
                        st.subheader("Outline")
                        st.markdown(plan)

                if "research_plan" in update:
                    with output_area:
                        st.subheader("Research (for outline)")
                        st.markdown("Collected context to inform drafting.")

                if "generate" in update:
                    draft = update["generate"].get("draft", "")
                    if draft:
                        last_draft = draft
                        st.session_state["last_draft"] = draft
                        with output_area:
                            st.subheader("Draft")
                            st.write(draft)

                if "reflect" in update:
                    critique = update["reflect"].get("critique", "")
                    if critique:
                        st.session_state["last_critique"] = critique
                        with output_area:
                            st.subheader("Critique")
                            st.write(critique)

                if "research_critique" in update:
                    with output_area:
                        st.subheader("Research (for critique)")
                        if tavily_client:
                            st.markdown("Fetched additional context to guide revisions.")
                        else:
                            st.markdown("Research disabled or unavailable; skipping.")

            status.update(label="Done!", state="complete")
        except Exception as e:
            status.update(label="Failed", state="error")
            st.exception(e)

    if last_draft:
        st.success("Final Draft")
        st.write(last_draft)
        st.download_button(
            "Download as .txt",
            data=last_draft,
            file_name="essay.txt",
            mime="text/plain",
        )
    else:
        st.info("No draft produced. Check your inputs and try again.")