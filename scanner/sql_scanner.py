"""
SQL Injection Scanner Module
Tests form inputs and URL parameters for SQL injection vulnerabilities.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse


# Common SQLi payloads — these trigger database errors or boolean-based responses
SQLI_PAYLOADS = [
    "'",
    "''",
    "`",
    "``",
    ",",
    '"',
    "\"\"",
    "/",
    "//",
    "\\",
    "\\\\",
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' OR 1=1--",
    "\" OR \"1\"=\"1",
    "1' ORDER BY 1--",
    "1' ORDER BY 2--",
    "1 AND 1=1",
    "1 AND 1=2",
]

# Error strings that indicate SQL errors from different databases
SQL_ERROR_SIGNATURES = [
    # MySQL
    "you have an error in your sql syntax",
    "warning: mysql",
    "mysql_fetch",
    "mysql_num_rows",
    # PostgreSQL
    "pg_query",
    "pg_exec",
    "postgresql",
    # MSSQL
    "unclosed quotation mark",
    "microsoft ole db provider for sql server",
    "microsoft sql server",
    # Oracle
    "ora-01756",
    "oracle error",
    # SQLite
    "sqlite_exception",
    "sqlite3.operationalerror",
    # Generic
    "sql syntax",
    "syntax error",
    "unexpected end of sql command",
    "quoted string not properly terminated",
    "supplied argument is not a valid mysql",
]


class SQLiScanner:
    def __init__(self, url, timeout=10, verbose=False):
        self.url = url
        self.timeout = timeout
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WebSentinel-Scanner/1.0 (Security Research)"
        })
        self.findings = []

    def _get_forms(self, url):
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, "html.parser")
            return soup.find_all("form")
        except Exception:
            return []

    def _get_form_details(self, form):
        details = {
            "action": form.attrs.get("action", "").lower(),
            "method": form.attrs.get("method", "get").lower(),
            "inputs": []
        }
        for input_tag in form.find_all(["input", "textarea"]):
            input_name = input_tag.attrs.get("name")
            input_type = input_tag.attrs.get("type", "text")
            if input_name:
                details["inputs"].append({
                    "type": input_type,
                    "name": input_name
                })
        return details

    def _is_vulnerable(self, response_text):
        """Check if the response contains SQL error signatures."""
        lower_response = response_text.lower()
        for error in SQL_ERROR_SIGNATURES:
            if error in lower_response:
                return True, error
        return False, None

    def _test_form_sqli(self, form_details, base_url):
        """Test form fields with SQLi payloads."""
        target_url = urljoin(base_url, form_details["action"]) or base_url

        for payload in SQLI_PAYLOADS:
            data = {}
            for input_field in form_details["inputs"]:
                if input_field["type"] != "submit":
                    data[input_field["name"]] = payload
                else:
                    data[input_field["name"]] = ""

            try:
                if form_details["method"] == "post":
                    response = self.session.post(target_url, data=data, timeout=self.timeout)
                else:
                    response = self.session.get(target_url, params=data, timeout=self.timeout)

                vulnerable, matched_error = self._is_vulnerable(response.text)
                if vulnerable:
                    return {
                        "type": "SQL Injection",
                        "severity": "CRITICAL",
                        "url": target_url,
                        "payload": payload,
                        "method": form_details["method"].upper(),
                        "matched_error": matched_error,
                        "description": (
                            "SQL Injection vulnerability detected. The application includes "
                            "unsanitized user input in database queries, potentially allowing "
                            "attackers to read, modify, or delete database contents."
                        ),
                        "recommendation": (
                            "Use parameterized queries / prepared statements. "
                            "Never concatenate user input directly into SQL queries. "
                            "Implement input validation and least-privilege DB accounts."
                        )
                    }
            except Exception:
                continue

        return None

    def _test_url_param_sqli(self):
        """Test URL parameters for SQL injection."""
        parsed = urlparse(self.url)
        params = parse_qs(parsed.query)

        if not params:
            return

        for param_name in params:
            for payload in SQLI_PAYLOADS[:5]:
                new_params = params.copy()
                new_params[param_name] = [payload]
                new_query = urlencode(new_params, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))

                try:
                    response = self.session.get(test_url, timeout=self.timeout)
                    vulnerable, matched_error = self._is_vulnerable(response.text)
                    if vulnerable:
                        self.findings.append({
                            "type": "SQL Injection - URL Parameter",
                            "severity": "CRITICAL",
                            "url": test_url,
                            "payload": payload,
                            "parameter": param_name,
                            "matched_error": matched_error,
                            "description": (
                                f"SQL Injection via URL parameter '{param_name}'. "
                                "Database error message exposed in response."
                            ),
                            "recommendation": (
                                "Use parameterized queries and sanitize all URL parameters."
                            )
                        })
                        break
                except Exception:
                    continue

    def scan(self):
        """Main scan method."""
        forms = self._get_forms(self.url)

        if self.verbose:
            print(f"    Found {len(forms)} form(s) on {self.url}")

        for form in forms:
            form_details = self._get_form_details(form)
            result = self._test_form_sqli(form_details, self.url)
            if result:
                self.findings.append(result)

        self._test_url_param_sqli()
        return self.findings
