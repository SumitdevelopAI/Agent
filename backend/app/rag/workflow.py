# backend/app/rag/workflow.py
from langgraph.graph import StateGraph
from typing import TypedDict, List, Any
from app.rag.retriever import retrieve_documents
from app.agents.compliance_agent import generate_response
import json
import re

class ComplianceState(TypedDict):
    query: str
    documents: List[dict]
    answer: Any

def retrieve_node(state: ComplianceState):
    docs = retrieve_documents(state["query"])
    state["documents"] = docs
    return state

def _normalize_llm_output(raw_output: Any) -> dict:
    """
    Ensure the LLM output is a dict with keys:
      - answer (str)
      - risk_level (str)
      - confidence (int)
    Accepts:
      - dict (returned directly)
      - JSON string (parse)
      - free text (fallback)
    """
    if isinstance(raw_output, dict):
        return raw_output

    # If string: try direct JSON parse
    if isinstance(raw_output, str):
        # 1) direct JSON
        try:
            parsed = json.loads(raw_output)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

        # 2) try to extract first {...} block (useful when model adds commentary)
        m = re.search(r"\{.*\}", raw_output, re.S)
        if m:
            try:
                parsed = json.loads(m.group(0))
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

        # 3) fallback: return as answer text with defaults
        return {
            "answer": raw_output.strip(),
            "risk_level": "Medium",
            "confidence": 50
        }

    # Other types: convert to string
    return {
        "answer": str(raw_output),
        "risk_level": "Medium",
        "confidence": 50
    }

def llm_node(state: ComplianceState):
    context = "\n".join([doc.get("text", "") for doc in state["documents"]])
    raw = generate_response(state["query"], context)

    normalized = _normalize_llm_output(raw)
    # Ensure fields exist with safe defaults
    normalized_answer = normalized.get("answer", "")
    normalized_risk = normalized.get("risk_level", "Medium")
    normalized_conf = normalized.get("confidence", 50)

    state["answer"] = {
        "answer": normalized_answer,
        "risk_level": normalized_risk,
        "confidence": normalized_conf
    }

    return state

graph = StateGraph(ComplianceState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("llm", llm_node)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "llm")

app_graph = graph.compile()

def run_workflow(query: str):

    initial_state: ComplianceState = {
        "query": query,
        "documents": [],
        "answer": {}
    }

    result = app_graph.invoke(initial_state)

    answer_obj = result.get("answer", {})

    return {
        "answer": answer_obj.get("answer", ""),
        "risk_level": answer_obj.get("risk_level", "Medium"),
        "confidence": answer_obj.get("confidence", 50),
        "sources": [
            {"document": doc.get("document"), "content": doc.get("text")}
            for doc in result.get("documents", [])
        ]
    }