
import json
from src.app import app

def test_api_contract():
    client = app.test_client()
    res = client.post(
        "/api/analyze",
        data=json.dumps({"symptoms": "Fever for 2 days, sore throat, cough"}),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert set(data.keys()) == {"conditions","next_steps","red_flags","disclaimer","raw_model_output"} or            set(data.keys()) == {"conditions","next_steps","red_flags","disclaimer"}
    assert isinstance(data["conditions"], list)
    assert isinstance(data["next_steps"], list)
    assert isinstance(data["red_flags"], list)
    assert isinstance(data["disclaimer"], str)
