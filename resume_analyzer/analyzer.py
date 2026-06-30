"""
AI Resume Analyzer — Core Engine
Uses Google Gemini API for NLP-based resume analysis.
Supports .txt, .tex, and .pdf file formats.
"""

import os
import json
import argparse
from pathlib import Path

from groq import Groq


# ─── File Extraction ──────────────────────────────────────────────────────────

def extract_text(file_path: str) -> tuple[str, str]:
    """
    Extract plain text from a resume file.
    Returns (text, file_type) where file_type is 'txt', 'tex', or 'pdf'.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()

    if ext in (".txt", ".tex"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read(), ext[1:]

    elif ext == ".pdf":
        try:
            import pdfplumber
        except ImportError:
            raise ImportError(
                "pdfplumber is required for PDF support.\n"
                "Install it with: pip install pdfplumber"
            )
        with pdfplumber.open(file_path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages), "pdf"

    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .txt, .tex, or .pdf")


# ─── Gemini API Analysis ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) reviewer and professional resume coach.

Analyze the resume and return ONLY a valid JSON object — no markdown fences, no explanation. Use this exact schema:

{
  "ats_score": <integer 0-100>,
  "skills_found": {
    "technical": ["list of technical skills"],
    "tools":     ["libraries, frameworks, platforms"],
    "soft":      ["soft skills, leadership, communication, etc."]
  },
  "keyword_gaps": ["important missing keywords for this domain"],
  "strengths":    ["what the resume does well"],
  "improvements": [
    { "priority": "high",   "suggestion": "..." },
    { "priority": "medium", "suggestion": "..." },
    { "priority": "low",    "suggestion": "..." }
  ],
  "summary": "2-3 sentence overall assessment"
}"""


def analyze_resume(text: str, file_type: str) -> dict:
    """
    Send resume text to Groq API and return structured analysis.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    format_note = {
        "tex": "Note: This resume is in LaTeX format. Parse through LaTeX markup to extract actual content (e.g. \\section{}, \\textbf{}, etc.).",
        "pdf": "Note: This text was extracted from a PDF resume.",
        "txt": "",
    }.get(file_type, "")

    user_message = f"{format_note}\n\nResume:\n{text}".strip()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


# ─── Terminal Display ─────────────────────────────────────────────────────────

RESET  = "\033[0m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"


def _score_color(score: int) -> str:
    if score >= 70:
        return GREEN
    elif score >= 50:
        return YELLOW
    return RED


def display_results(results: dict) -> None:
    """Pretty-print analysis results to the terminal."""
    print("\n" + "=" * 62)
    print(f"{BOLD}           AI RESUME ANALYZER — RESULTS{RESET}")
    print("=" * 62)

    # ATS Score
    score = results.get("ats_score", 0)
    filled = score // 5
    bar = "█" * filled + "░" * (20 - filled)
    color = _score_color(score)
    print(f"\n{BOLD}📊 ATS Score:{RESET} {color}{score}/100{RESET}")
    print(f"   [{bar}]")

    # Skills
    skills = results.get("skills_found", {})
    print(f"\n{BOLD}🔧 Technical Skills:{RESET}  {', '.join(skills.get('technical', [])) or 'None found'}")
    print(f"{BOLD}🛠  Tools/Frameworks:{RESET}  {', '.join(skills.get('tools', [])) or 'None found'}")
    print(f"{BOLD}💡 Soft Skills:{RESET}       {', '.join(skills.get('soft', [])) or 'None found'}")

    # Keyword Gaps
    gaps = results.get("keyword_gaps", [])
    if gaps:
        print(f"\n{BOLD}⚠  Keyword Gaps:{RESET}")
        print(f"   {', '.join(gaps)}")

    # Strengths
    strengths = results.get("strengths", [])
    if strengths:
        print(f"\n{BOLD}✅ Strengths:{RESET}")
        for s in strengths:
            print(f"   • {s}")

    # Improvements
    improvements = results.get("improvements", [])
    if improvements:
        print(f"\n{BOLD}📝 Improvement Suggestions:{RESET}")
        icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        for imp in improvements:
            p = imp.get("priority", "low")
            print(f"   {icons.get(p, '⚪')} [{p.upper():6}] {imp['suggestion']}")

    # Summary
    summary = results.get("summary", "")
    if summary:
        print(f"\n{BOLD}💬 Summary:{RESET}")
        print(f"   {summary}")

    print("\n" + "=" * 62 + "\n")


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Analyzer — powered by Google Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyzer.py resume.txt
  python analyzer.py resume.pdf
  python analyzer.py resume.tex
  python analyzer.py resume.pdf --output results.json
        """,
    )
    parser.add_argument("file", help="Path to resume (.txt, .tex, .pdf)")
    parser.add_argument(
        "--output", "-o", metavar="FILE",
        help="Save JSON results to a file", default=None
    )
    args = parser.parse_args()

    # API key check
    if not os.environ.get("GROQ_API_KEY"):
        print(f"{RED}❌ Error: GROQ_API_KEY is not set.{RESET}")
        print("   Add your Groq API key to .env file as: GROQ_API_KEY=gsk_...")
        return

    print(f"📂 Reading: {args.file}")
    text, file_type = extract_text(args.file)
    print(f"✅ Extracted {len(text):,} characters from {file_type.upper()} file")
    print("🤖 Analyzing with Gemini API…")

    results = analyze_resume(text, file_type)
    display_results(results)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"💾 Results saved to {args.output}\n")


if __name__ == "__main__":
    main()