from typing import Dict, Any
from app.rag.vector_store import search_similar
from app.rag.embeddings import embed_text
from app.agents.compliance_agent import generate_response


SIMILARITY_THRESHOLD = 0.40


def gap_analysis(internal_doc_id: int, regulation_requirement: str) -> Dict[str, Any]:

    query_embedding = embed_text(regulation_requirement)

    internal_matches = search_similar(
        query_embedding,
        top_k=5,
        doc_type="internal",
        document_id=internal_doc_id
    )

    if not internal_matches:
        return {
            "requirement": regulation_requirement,
            "analysis": {
                "compliance_status": "Non-Compliant",
                "risk_level": "High",
                "confidence": 95,
                "similarity_score": 0,
                "justification": "No internal policy found matching regulation requirement."
            }
        }

    filtered_matches = [
        m for m in internal_matches
        if m.get("similarity_score", 1) <= SIMILARITY_THRESHOLD
    ]

    if not filtered_matches:
        return {
            "requirement": regulation_requirement,
            "analysis": {
                "compliance_status": "Non-Compliant",
                "risk_level": "High",
                "confidence": 85,
                "similarity_score": internal_matches[0].get("similarity_score", 1),
                "justification": "Internal policies exist but semantic similarity is weak."
            }
        }

    sorted_matches = sorted(
        filtered_matches,
        key=lambda x: x["similarity_score"]
    )

    context = "\n\n".join(
        match["text"] for match in sorted_matches
    )

    # ✅ SAFE CALL (no keyword)
    llm_result = generate_response(
        regulation_requirement,
        context
    )

    best_similarity = sorted_matches[0]["similarity_score"]

    if llm_result["compliance_status"] == "Compliant" and best_similarity < 0.25:
        llm_result["risk_level"] = "Low"

    if llm_result["compliance_status"] == "Non-Compliant":
        llm_result["risk_level"] = "High"

    llm_result["similarity_score"] = round(best_similarity, 4)

    return {
        "requirement": regulation_requirement,
        "analysis": llm_result
    }