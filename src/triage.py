import re
from typing import Optional
from .schema import AnalysisResponse

RED_FLAG_PATTERNS = [
    r"\bchest pain\b",
    r"\bshort(ness)? of breath\b",
    r"\bdifficulty breathing\b",
    r"\bone[- ]sided weakness\b",
    r"\bslurred speech\b",
    r"\bconfusion\b",
    r"\bblue (lips|face)\b",
    r"\bsevere bleeding\b",
    r"\b(stiff neck with fever|meningitis)\b",
    r"\bsuicidal (thought|ideation|intent)\b",
]

URGENT_GUIDANCE = [
    "If symptoms are severe, sudden, or worsening, seek urgent care immediately.",
    "Call local emergency services if experiencing life-threatening symptoms (e.g., difficulty breathing, chest pain).",
]

PEDIATRIC_CAUTION = "For children, prolonged fever, lethargy, poor feeding, or dehydration require prompt clinician evaluation."

def _find_matches(text: str):
    found = []
    for pat in RED_FLAG_PATTERNS:
        if re.search(pat, text, flags=re.IGNORECASE):
            found.append(pat)
    return found

def apply_server_side_triage(symptoms_text: str, llm_resp: AnalysisResponse, age: Optional[int] = None) -> AnalysisResponse:
    matches = _find_matches(symptoms_text)

    red_flags = list(llm_resp.red_flags)
    next_steps = list(llm_resp.next_steps)

    for line in URGENT_GUIDANCE:
        if line not in next_steps:
            next_steps.append(line)

    if matches:
        extra = [
            "Concerning symptom pattern detected based on your description.",
            "Seek urgent care for severe, sudden, or persistent symptoms.",
        ]
        for e in extra:
            if e not in red_flags:
                red_flags.append(e)

    if age is not None and age < 18 and PEDIATRIC_CAUTION not in next_steps:
        next_steps.append(PEDIATRIC_CAUTION)

    llm_resp.red_flags = red_flags
    llm_resp.next_steps = next_steps
    return llm_resp
