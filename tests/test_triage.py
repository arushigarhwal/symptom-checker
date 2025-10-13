
from src.triage import apply_server_side_triage
from src.schema import AnalysisResponse

def test_triage_adds_urgent_guidance():
    resp = AnalysisResponse(conditions=[], next_steps=[], red_flags=[], disclaimer="x")
    out = apply_server_side_triage("sudden chest pain", resp)
    assert any("urgent" in s.lower() for s in out.next_steps)
    assert out.red_flags, "should add something to red flags"
