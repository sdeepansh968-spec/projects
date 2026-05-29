"""
XSS (Cross-Site Scripting) Scanner Module
Tests form inputs and URL parameters for reflected XSS vulnerabilities.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse


# Common XSS payloads used in real penetration testing
XSS_PAYLOADS = [
    '<script>alert("XSS")</script>',
    '"><script>alert(1)</script>',
    "'><script>alert(1)</script>",
    '<img src=x onerror=alert(1)>',
    '<svg onload=alert(1)>',
    '"><img src=x onerror=alert(1)>',
    'javascript:alert(1)',
    '<body onload=alert(1)>',
]


class XSSScanner:
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
        """Extract all forms from a page."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, "html.parser")
            return soup.find_all("form")
        except Exception:
            return []

    def _get_form_details(self, form):
        """Extract form action, method, and inputs."""
        details = {
            "action": form.attrs.get("action", "").lower(),
            "method": form.attrs.get("method", "get").lower(),
            "inputs": []
        }
        for input_tag in form.find_all(["input", "textarea"]):
            input_type = input_tag.attrs.get("type", "text")
            input_name = input_tag.attrs.get("name")
            if input_name:
                details["inputs"].append({
                    "type": input_type,
                    "name": input_name
                })
        return details

    def _test_form_xss(self, form_details, base_url):
        """Submit form with XSS payloads and check if they're reflected."""
        target_url = urljoin(base_url, form_details["action"]) or base_url

        for payload in XSS_PAYLOADS:
            data = {}
            for input_field in form_details["inputs"]:
                if input_field["type"] in ("text", "search", "email", "url", "textarea"):
                    data[input_field["name"]] = payload
                elif input_field["type"] == "hidden":
                    data[input_field["name"]] = payload
                else:
                    data[input_field["name"]] = "test"

            try:
                if form_details["method"] == "post":
                    response = self.session.post(target_url, data=data, timeout=self.timeout)
                else:
                    response = self.session.get(target_url, params=data, timeout=self.timeout)

                # Check if payload is reflected in response
                if payload in response.text:
                    return {
                        "type": "Cross-Site Scripting (XSS)",
                        "severity": "HIGH",
                        "url": target_url,
                        "payload": payload,
                        "method": form_details["method"].upper(),
                        "description": (
                            "Reflected XSS detected. The application returns user-supplied "
                            "input without proper sanitization, allowing script injection."
                        ),
                        "recommendation": (
                            "Implement output encoding (HTML entity encoding), "
                            "use Content-Security-Policy headers, and validate all inputs."
                        )
                    }
            except Exception:
                continue

        return None

    def _test_url_param_xss(self):
        """Test URL parameters for XSS."""
        parsed = urlparse(self.url)
        params = parse_qs(parsed.query)

        if not params:
            return

        for param_name in params:
            for payload in XSS_PAYLOADS[:3]:  # Test with first 3 payloads for speed
                new_params = params.copy()
                new_params[param_name] = [payload]
                new_query = urlencode(new_params, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))

                try:
                    response = self.session.get(test_url, timeout=self.timeout)
                    if payload in response.text:
                        self.findings.append({
                            "type": "Cross-Site Scripting (XSS) - URL Parameter",
                            "severity": "HIGH",
                            "url": test_url,
                            "payload": payload,
                            "parameter": param_name,
                            "description": (
                                f"XSS via URL parameter '{param_name}'. "
                                "Payload is reflected directly in the response."
                            ),
                            "recommendation": (
                                "Sanitize and encode all URL parameters before rendering in HTML."
                            )
                        })
                        break  # One finding per param is enough
                except Exception:
                    continue

    def scan(self):
        """Main scan method."""
        forms = self._get_forms(self.url)

        if self.verbose:
            print(f"    Found {len(forms)} form(s) on {self.url}")

        for form in forms:
            form_details = self._get_form_details(form)
            result = self._test_form_xss(form_details, self.url)
            if result:
                self.findings.append(result)

        self._test_url_param_xss()
        return self.findings
