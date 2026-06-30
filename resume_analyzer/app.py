"""
AI Resume Analyzer — Flask Web Interface
Run with: python app.py
Then open: http://localhost:5000
"""

import os
import tempfile

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from analyzer import extract_text, analyze_resume

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024   # 5 MB upload limit

ALLOWED_EXTENSIONS = {"txt", "tex", "pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Accepts either:
      • multipart/form-data  with a 'file' field  (.txt / .tex / .pdf)
      • application/json     with a 'text' field  (plain pasted text)
    Returns JSON analysis from Gemini.
    """
    if not os.environ.get("GROQ_API_KEY"):
        return jsonify({"error": "GROQ_API_KEY is not configured on the server."}), 500

    # ── JSON / text paste path ───────────────────────────────────────────────
    if request.is_json:
        body = request.get_json(silent=True) or {}
        text = body.get("text", "").strip()
        if not text:
            return jsonify({"error": "No text provided."}), 400
        file_type = "txt"

    # ── File upload path ─────────────────────────────────────────────────────
    elif "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected."}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Only .txt, .tex, and .pdf files are supported."}), 400

        suffix = "." + secure_filename(file.filename).rsplit(".", 1)[-1].lower()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp_path = tmp.name
            file.save(tmp_path)

        try:
            text, file_type = extract_text(tmp_path)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400
        finally:
            os.unlink(tmp_path)

    else:
        return jsonify({"error": "Send a file or JSON body with 'text'."}), 400

    # ── Call Gemini ───────────────────────────────────────────────────────────
    try:
        results = analyze_resume(text, file_type)
    except Exception as exc:
        return jsonify({"error": f"Analysis failed: {exc}"}), 500

    return jsonify(results)


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug, port=port)