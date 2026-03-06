from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import json
import re
from typing import Dict

MODEL_NAME = "google/flan-t5-base"

_device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(_device)

FINANCIAL_KEYWORDS = [
    "gdpr", "ai act", "fca", "bank", "financial",
    "compliance", "regulation", "aml", "kyc",
    "risk", "dora", "basel", "psd2"
]


def is_financial_query(query: str) -> bool:
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in FINANCIAL_KEYWORDS)


def build_prompt(query: str, context: str) -> str:
    return f"""
You are a senior financial regulatory compliance auditor.

Task:
{query}

Rules:
- Use ONLY the provided internal policy context.
- Do NOT invent missing controls.
- If no relevant evidence → classify as High Risk.

Return STRICT JSON:

{{
  "summary": "...",
  "obligations": "...",
  "risk_areas": "...",
  "missing_elements": "...",
  "risk_level": "Low | Medium | High",
  "confidence": 0-100
}}

Internal Policy Context:
{context}
"""


def extract_json(text: str) -> Dict:
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass

    return {
        "summary": "",
        "obligations": "",
        "risk_areas": "",
        "missing_elements": "",
        "risk_level": "Medium",
        "confidence": 50
    }


def grounded_confidence(justification: str, context: str) -> int:
    if not context.strip():
        return 10

    overlap = set(justification.lower().split()) & set(context.lower().split())
    ratio = len(overlap) / max(1, len(justification.split()))

    return min(95, max(25, int(ratio * 120)))


def generate_response(query: str, context: str) -> Dict:
    """
    Generic compliance analysis function.
    Supports document analysis + gap detection.
    """

    if not context.strip():
        return {
            "summary": "No internal policy evidence found.",
            "obligations": "",
            "risk_areas": "",
            "missing_elements": "",
            "risk_level": "High",
            "confidence": 95
        }

    prompt = build_prompt(query, context)

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    ).to(_device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=400,
            num_beams=5,
            temperature=0.2,
            repetition_penalty=1.15,
            early_stopping=True
        )

    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    parsed = extract_json(response_text)

    recalculated_conf = grounded_confidence(
        parsed.get("summary", "") + parsed.get("risk_areas", ""),
        context
    )

    parsed["confidence"] = recalculated_conf

    return parsed