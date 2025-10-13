from typing import Optional

def build_messages(symptoms: str, age: Optional[int], duration_days: Optional[int], disclaimer: str):
    system = (
        "You are a cautious medical information assistant for EDUCATIONAL purposes ONLY. "
        "You are NOT a doctor, do NOT provide diagnoses, and do NOT prescribe or suggest medication dosages. "
        "You help the user understand POSSIBLE conditions and SAFE next steps, and ALWAYS include red-flag guidance. "
        "ALWAYS output STRICT JSON with keys: conditions (list of {name, likelihood_note, evidence[list]}), "
        "next_steps (list of strings), red_flags (list of strings), disclaimer (string)."
    )

    user_context = {
        "symptoms": symptoms,
        "age": age,
        "duration_days": duration_days,
    }

    schema = {
        "conditions": [{"name": "string", "likelihood_note": "string", "evidence": ["string", "..."]}],
        "next_steps": ["string", "..."],
        "red_flags": ["string", "..."],
        "disclaimer": "string"
    }

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": f"User input (JSON): {user_context}"},
        {"role": "system", "content": f"Return JSON ONLY. Schema: {schema}  Always include this exact disclaimer string: {disclaimer} "},
    ]
