# 🤖 AI Resume Analyzer

A Python-based resume analysis tool powered by **Claude AI (Anthropic API)**.  
Parses resumes, extracts skills, scores ATS compatibility, identifies keyword gaps, and generates prioritized improvement suggestions.

Supports **.txt · .tex (LaTeX) · .pdf** — usable as a CLI tool or via a local web interface.

---

## ✨ Features

| Feature | Description |
|---|---|
| **ATS Score (0–100)** | Measures how well the resume would pass Applicant Tracking Systems |
| **Skill Extraction** | Auto-detects technical skills, tools/frameworks, and soft skills |
| **Keyword Gap Analysis** | Finds important missing keywords for the target domain |
| **Improvement Suggestions** | Priority-tagged recommendations (🔴 High / 🟡 Medium / 🟢 Low) |
| **Multi-format Support** | Reads `.txt`, `.tex` (LaTeX), and `.pdf` files |
| **CLI + Web UI** | Terminal output or browser-based interface |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/your-username/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
```bash
cp .env.example .env
# Open .env and add your Anthropic API key
```

Get your API key at [console.anthropic.com](https://console.anthropic.com)

---

## 🖥 Usage

### CLI Mode
```bash
# Analyze a resume (terminal output)
python analyzer.py resume.txt
python analyzer.py resume.pdf
python analyzer.py resume.tex

# Save results to JSON
python analyzer.py resume.pdf --output results.json

# Try the included sample
python analyzer.py sample_resume.txt
```

**Sample CLI output:**
```
📂 Reading: resume.pdf
✅ Extracted 1,243 characters from PDF file
🤖 Analyzing with Claude API…

══════════════════════════════════════════════════════════════
             AI RESUME ANALYZER — RESULTS
══════════════════════════════════════════════════════════════

📊 ATS Score: 72/100
   [██████████████░░░░░░]

🔧 Technical Skills:  Python, JavaScript, C, SQL
🛠  Tools/Frameworks:  Flask, React, Git, Burp Suite
💡 Soft Skills:       Communication, Problem Solving

⚠  Keyword Gaps:
   Docker, REST APIs, CI/CD, AWS, System Design

✅ Strengths:
   • Strong hands-on security lab experience
   • Clear project impact with technical depth

📝 Improvement Suggestions:
   🔴 [HIGH  ] Add quantified metrics to project descriptions
   🟡 [MEDIUM] Include a professional summary section
   🟢 [LOW   ] Mention open-source contributions if any

💬 Summary:
   Solid technical foundation with practical cybersecurity
   experience. Adding measurable outcomes and expanding
   cloud/DevOps keywords will improve ATS performance.
══════════════════════════════════════════════════════════════
```

### Web UI Mode
```bash
python app.py
# Open http://localhost:5000
```

The web interface supports:
- Drag-and-drop file upload
- Paste-text input
- Animated ATS score bar
- Color-coded skill tags and improvement suggestions

---

## 📁 Project Structure

```
ai-resume-analyzer/
├── analyzer.py          # Core analysis engine + CLI entry point
├── app.py               # Flask web server
├── templates/
│   └── index.html       # Dark-themed web UI
├── requirements.txt
├── sample_resume.txt    # Test resume to try immediately
├── .env.example         # API key template
└── .gitignore
```

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Claude API** (`claude-sonnet-4-6`) — NLP analysis via prompt engineering
- **Flask** — lightweight web server
- **pdfplumber** — PDF text extraction
- **python-dotenv** — environment variable management

---

## 🔧 How It Works

1. **File Parsing** — `extract_text()` reads `.txt`/`.tex` directly; uses `pdfplumber` for `.pdf`
2. **Prompt Engineering** — Resume text is sent to Claude with a structured system prompt requesting JSON output
3. **Response Parsing** — Claude's JSON response is cleaned (strips markdown fences) and parsed
4. **Display** — Results rendered in terminal with ANSI colors or in the browser via Flask

```python
# Core analysis call
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1500,
    system=SYSTEM_PROMPT,       # Structured JSON schema instruction
    messages=[{"role": "user", "content": resume_text}]
)
results = json.loads(response.content[0].text)
```

---

## 📝 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ Yes | — | Your Anthropic API key |
| `PORT` | No | `5000` | Flask server port |
| `FLASK_DEBUG` | No | `true` | Enable Flask debug mode |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

> Built as a portfolio project demonstrating Claude API integration, prompt engineering, and multi-format file parsing.
