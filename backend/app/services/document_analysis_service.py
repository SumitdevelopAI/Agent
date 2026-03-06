from app.rag.embeddings import embed_text
from app.rag.vector_store import search_similar
from app.agents.compliance_agent import generate_response


def analyze_document(document_id: int):
    """
    Perform full intelligent analysis of uploaded document.
    """

    # Retrieve top internal chunks
    query_embedding = embed_text("Summarize regulatory and financial obligations")

    matches = search_similar(
        query_embedding,
        top_k=8,
        document_id=document_id
    )

    if not matches:
        return {
            "summary": "No meaningful content found.",
            "risk_level": "Unknown",
            "confidence": 20
        }

    context = "\n\n".join([m["text"] for m in matches])

    # Generate summary and risk assessment using the compliance agent
    prompt = f"""You are a compliance analyst. Based on the following document content, provide a concise summary of key regulatory
and financial obligations, and assess the overall risk level (Low, Medium, High) for non-compliance. Be specific about which obligations are most critical.
Document Content:
{context}
"""
    result = generate_response(
    query="""
    Perform detailed compliance analysis:
    - Summarize document
    - Identify financial/regulatory obligations
    - Highlight risk areas
    - Detect missing compliance elements
    """,
    context=context
)

    return {
        "summary": result.get("summary", ""),
        "risk_level": result.get("risk_level", "Unknown"),
        "confidence": result.get("confidence", 0)
    }