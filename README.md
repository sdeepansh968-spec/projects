# 🛡️ WebSentinel — Web Vulnerability Scanner

> A Python-based web vulnerability scanner for identifying common security misconfigurations and vulnerabilities in web applications. Built for educational purposes and authorized penetration testing.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Security](https://img.shields.io/badge/Domain-Cybersecurity-red?style=flat-square)

---

## 📌 About

WebSentinel is a modular web vulnerability scanner that automates detection of common vulnerabilities outlined in the **OWASP Top 10**. It is designed to help security researchers and developers identify weaknesses in web applications they are authorized to test.

This project was built to understand how real-world scanners like **Burp Suite** and **OWASP ZAP** work under the hood — by building one from scratch.

---

## 🔍 Features

| Module | Vulnerability | OWASP Category |
|--------|--------------|----------------|
| XSS Scanner | Reflected Cross-Site Scripting | A03: Injection |
| SQLi Scanner | SQL Injection via error-based detection | A03: Injection |
| Header Scanner | Missing/misconfigured HTTP security headers | A05: Security Misconfiguration |
| Directory Scanner | Exposed admin panels, config files, backups | A05: Security Misconfiguration |

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/sdeepansh968-spec/projects.git
cd web-vuln-scanner

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 💻 Usage

### Basic scan (all modules)
```bash
python main.py -u http://testphp.vulnweb.com
```

### Run specific scan type
```bash
python main.py -u http://testphp.vulnweb.com -s xss
python main.py -u http://testphp.vulnweb.com -s sqli
python main.py -u http://testphp.vulnweb.com -s headers
python main.py -u http://testphp.vulnweb.com -s dirs
```

### Save report to file
```bash
python main.py -u http://testphp.vulnweb.com -o report.txt
```

### Verbose mode
```bash
python main.py -u http://testphp.vulnweb.com -v
```

### All options
```
usage: main.py [-h] -u URL [-s {all,xss,sqli,headers,dirs}] [-o OUTPUT] [-v] [--timeout TIMEOUT]

  -u, --url       Target URL (required)
  -s, --scan      Scan type: all | xss | sqli | headers | dirs (default: all)
  -o, --output    Save report to file
  -v, --verbose   Verbose output
  --timeout       Request timeout in seconds (default: 10)
```

---

## 📸 Sample Output

```
[*] Running XSS Scanner...
[+] XSS Scanner complete — 2 finding(s)

[*] Running SQL Injection Scanner...
[+] SQL Injection Scanner complete — 1 finding(s)

======================================================================
  SCAN RESULTS — WebSentinel
======================================================================
  Target  : http://testphp.vulnweb.com
  Total   : 3 finding(s)
======================================================================

  [1] Cross-Site Scripting (XSS)
  Severity : HIGH
  URL      : http://testphp.vulnweb.com/search.php
  Payload  : <script>alert("XSS")</script>
  Description  : Reflected XSS detected. The application returns user-supplied
                 input without proper sanitization...
  Recommendation: Implement output encoding, use CSP headers...
```

---

## 🧪 Safe Testing

**Only scan systems you own or have explicit written permission to test.**

You can safely test this tool on intentionally vulnerable applications:
- [http://testphp.vulnweb.com](http://testphp.vulnweb.com) — Acunetix test site
- [DVWA](https://github.com/digininja/DVWA) — Damn Vulnerable Web App (run locally)
- [WebGoat](https://github.com/WebGoat/WebGoat) — OWASP WebGoat (run locally)

---

## 🏗️ Project Structure

```
web-vuln-scanner/
├── main.py                  # Entry point, CLI argument handling
├── requirements.txt         # Dependencies
├── scanner/
│   ├── xss_scanner.py       # XSS detection module
│   ├── sql_scanner.py       # SQL Injection detection module
│   ├── header_scanner.py    # Security headers audit module
│   └── dir_scanner.py       # Directory & sensitive file enumeration
├── reports/
│   └── report_generator.py  # Terminal + file report formatting
└── utils/
    └── logger.py            # Colored terminal logging
```

---

## 🔬 How It Works

### XSS Scanner
Crawls all HTML forms on the target page, injects common XSS payloads (e.g., `<script>alert(1)</script>`, `<img src=x onerror=alert(1)>`), and checks if the payload is reflected in the response body.

### SQL Injection Scanner
Submits SQL metacharacters and boolean-based payloads (`' OR 1=1--`) into form fields and URL parameters. Detects vulnerabilities by matching known database error messages (MySQL, PostgreSQL, MSSQL, Oracle) in the response.

### Security Headers Scanner
Sends a GET request and inspects response headers against OWASP-recommended security headers including CSP, HSTS, X-Frame-Options, and X-Content-Type-Options. Also flags information-disclosure headers like `Server` and `X-Powered-By`.

### Directory Scanner
Uses a curated wordlist with multithreading (10 workers) to probe for exposed admin panels, backup files, config files, and sensitive paths. Reports HTTP 200/403/401 responses as findings.

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **requests** — HTTP client for sending crafted requests
- **BeautifulSoup4** — HTML parsing to extract forms and inputs
- **concurrent.futures** — Multithreading for fast directory scanning
- **argparse** — CLI interface

---

## ⚠️ Disclaimer

This tool is developed for **educational purposes** and **authorized security testing only**.  
Using this tool against systems without explicit written authorization is **illegal** and **unethical**.  
The author is not responsible for any misuse of this software.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
