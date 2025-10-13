import requests, json
from .schema import AnalysisResponse
from .prompts import build_messages

def analyze_symptoms_with_llm(symptoms, age, duration_days, model_name, disclaimer):
    messages = build_messages(symptoms, age, duration_days, disclaimer)
    prompt = "\n".join([m["content"] for m in messages])

    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model_name or "qwen2.5:7b-instruct-q4_K_M", "prompt": prompt, "stream": False},
        timeout=120
    )
    r.raise_for_status()
    content = r.json().get("response", "").strip()

    try:
        data = json.loads(content)
        return AnalysisResponse.model_validate(data)
    except Exception:
        return AnalysisResponse(
            conditions=[{"name": "Unspecified — further evaluation needed", "likelihood_note": "Insufficient detail", "evidence": []}],
            next_steps=["Monitor symptoms, rest, hydrate", "Consult a qualified clinician for evaluation"],
            red_flags=["Severe, sudden, or worsening symptoms", "Difficulty breathing, chest pain, confusion, blue lips/face"],
            disclaimer=disclaimer,
            raw_model_output=content
        )
