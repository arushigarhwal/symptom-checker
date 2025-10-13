import os
import sqlite3
from contextlib import closing
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from .schema import AnalysisRequest, AnalysisResponse, SafeError
from .llm import analyze_symptoms_with_llm
from .triage import apply_server_side_triage
from .utils import mask_text, ensure_db

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")

MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b-instruct-q4_K_M")
SHOW_UI = os.getenv("SHOW_UI", "true").lower() == "true"
DB_PATH = os.getenv("DB_PATH", os.path.join(os.getcwd(), "symptom_history.db"))

DISCLAIMER = (
    "Educational use only. This is NOT a diagnosis and does not replace professional medical advice. "
    "Call your local emergency number or seek urgent care for severe, sudden, or worsening symptoms."
)

# Flask 3.x safe: init DB at import time
ensure_db(DB_PATH)

def _save_entry(symptoms: str, resp: AnalysisResponse):
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn, closing(conn.cursor()) as cur:
            cur.execute(
                "INSERT INTO history (ts, symptoms, response_json) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat(timespec="seconds"), symptoms, resp.model_dump_json()),
            )
            conn.commit()
    except Exception:
        pass

@app.get("/")
def home():
    if not SHOW_UI:
        return jsonify({"message": "UI disabled. Use /api/analyze POST."}), 200
    return render_template("index.html")

@app.post("/api/analyze")
def api_analyze():
    try:
        payload = request.get_json(force=True, silent=False)
        req = AnalysisRequest(**payload)
    except Exception as e:
        return jsonify(SafeError(error="Invalid input", details=str(e)).model_dump()), 400

    llm_resp = analyze_symptoms_with_llm(
        symptoms=req.symptoms,
        age=req.age,
        duration_days=req.duration_days,
        model_name=MODEL_NAME,
        disclaimer=DISCLAIMER,
    )

    final_resp = apply_server_side_triage(req.symptoms, llm_resp, age=req.age)
    final_resp.disclaimer = DISCLAIMER

    _save_entry(req.symptoms, final_resp)
    return jsonify(final_resp.model_dump()), 200

@app.post("/analyze")
def form_analyze():
    if not SHOW_UI:
        return jsonify({"message": "UI disabled. Use /api/analyze POST."}), 200

    symptoms = request.form.get("symptoms", "").strip()
    age_val = request.form.get("age", "").strip()
    duration_val = request.form.get("duration_days", "").strip()

    try:
        req = AnalysisRequest(
            symptoms=symptoms,
            age=int(age_val) if age_val else None,
            duration_days=int(duration_val) if duration_val else None,
        )
    except Exception as e:
        return render_template("index.html", error=f"Invalid input: {e}")

    llm_resp = analyze_symptoms_with_llm(
        symptoms=req.symptoms,
        age=req.age,
        duration_days=req.duration_days,
        model_name=MODEL_NAME,
        disclaimer=DISCLAIMER,
    )

    final_resp = apply_server_side_triage(req.symptoms, llm_resp, age=req.age)
    final_resp.disclaimer = DISCLAIMER

    _save_entry(req.symptoms, final_resp)

    return render_template(
        "index.html",
        result=final_resp,
        masked_input=mask_text(req.symptoms, keep=400)
    )

@app.get("/history")
def history():
    if not SHOW_UI:
        return jsonify({"message": "UI disabled."}), 200
    rows = []
    with closing(sqlite3.connect(DB_PATH)) as conn, closing(conn.cursor()) as cur:
        cur.execute("SELECT id, ts, symptoms FROM history ORDER BY id DESC LIMIT 50")
        rows = cur.fetchall()
    return render_template("history.html", rows=rows)

@app.get("/history/<int:item_id>")
def history_item(item_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn, closing(conn.cursor()) as cur:
        cur.execute("SELECT response_json, symptoms, ts FROM history WHERE id = ?", (item_id,))
        row = cur.fetchone()
        if not row:
            return render_template("history_item.html", error="Not found")
        response_json, symptoms, ts = row
    return render_template("history_item.html", response_json=response_json, symptoms=symptoms, ts=ts)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
