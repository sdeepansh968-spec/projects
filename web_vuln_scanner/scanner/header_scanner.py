"""
Security Headers Scanner Module
Checks for presence and proper configuration of HTTP security headers.
"""

import requests


# Security headers and what they do — good to know for interviews!
SECURITY_HEADERS = {
    "Strict-Transport-Security": {
        "severity": "HIGH",
        "description": (
            "HSTS header missing. Without this, attackers can perform SSL stripping attacks, "
            "downgrading HTTPS connections to HTTP."
        ),
        "recommendation": (
            "Add: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload"
        )
    },
    "Content-Security-Policy": {
        "severity": "HIGH",
        "description": (
            "CSP header missing. This header prevents XSS and data injection attacks "
            "by specifying which sources browsers should execute scripts from."
        ),
        "recommendation": (
            "Add a Content-Security-Policy header. Start with: "
            "Content-Security-Policy: default-src 'self'"
        )
    },
    "X-Frame-Options": {
        "severity": "MEDIUM",
        "description": (
            "X-Frame-Options header missing. The site may be vulnerable to Clickjacking attacks "
            "where attackers embed it in an iframe to trick users."
        ),
        "recommendation": (
            "Add: X-Frame-Options: DENY  or  X-Frame-Options: SAMEORIGIN"
        )
    },
    "X-Content-Type-Options": {
        "severity": "MEDIUM",
        "description": (
            "X-Content-Type-Options header missing. Browsers may perform MIME-type sniffing, "
            "potentially executing malicious files as a different content type."
        ),
        "recommendation": (
            "Add: X-Content-Type-Options: nosniff"
        )
    },
    "Referrer-Policy": {
        "severity": "LOW",
        "description": (
            "Referrer-Policy header missing. Sensitive URL information may leak to third parties "
            "through the Referer header."
        ),
        "recommendation": (
            "Add: Referrer-Policy: strict-origin-when-cross-origin"
        )
    },
    "Permissions-Policy": {
        "severity": "LOW",
        "description": (
            "Permissions-Policy header missing. Browser features like camera, microphone, "
            "and geolocation are not explicitly restricted."
        ),
        "recommendation": (
            "Add: Permissions-Policy: camera=(), microphone=(), geolocation=()"
        )
    },
}

# Headers that should NOT be present (info disclosure)
DANGEROUS_HEADERS = {
    "Server": {
        "severity": "LOW",
        "description": "Server header exposes web server technology and version, helping attackers target known CVEs.",
        "recommendation": "Remove or obfuscate the Server header in your web server configuration."
    },
    "X-Powered-By": {
        "severity": "LOW",
        "description": "X-Powered-By header leaks backend technology (e.g., PHP/7.4), aiding attackers.",
        "recommendation": "Remove X-Powered-By header. In PHP: expose_php = Off"
    },
    "X-AspNet-Version": {
        "severity": "LOW",
        "description": "ASP.NET version information is exposed, revealing the framework version.",
        "recommendation": "Set <httpRuntime enableVersionHeader='false' /> in web.config"
    },
}


class HeaderScanner:
    def __init__(self, url, timeout=10, verbose=False):
        self.url = url
        self.timeout = timeout
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WebSentinel-Scanner/1.0 (Security Research)"
        })
        self.findings = []

    def scan(self):
        """Check response headers against security best practices."""
        try:
            response = self.session.get(self.url, timeout=self.timeout)
        except requests.RequestException as e:
            return [{"type": "Connection Error", "severity": "INFO", "description": str(e)}]

        headers = response.headers

        # Check for missing security headers
        for header_name, info in SECURITY_HEADERS.items():
            if header_name not in headers:
                self.findings.append({
                    "type": f"Missing Security Header: {header_name}",
                    "severity": info["severity"],
                    "url": self.url,
                    "description": info["description"],
                    "recommendation": info["recommendation"]
                })
            elif self.verbose:
                print(f"    [OK] {header_name}: {headers[header_name][:60]}")

        # Check for dangerous headers that reveal info
        for header_name, info in DANGEROUS_HEADERS.items():
            if header_name in headers:
                self.findings.append({
                    "type": f"Information Disclosure Header: {header_name}",
                    "severity": info["severity"],
                    "url": self.url,
                    "header_value": headers[header_name],
                    "description": info["description"],
                    "recommendation": info["recommendation"]
                })

        # Check for HTTPS
        if self.url.startswith("http://"):
            self.findings.append({
                "type": "Insecure Protocol (HTTP)",
                "severity": "HIGH",
                "url": self.url,
                "description": (
                    "Site is served over HTTP (unencrypted). All data including credentials "
                    "can be intercepted via Man-in-the-Middle attacks."
                ),
                "recommendation": "Enforce HTTPS with a valid TLS certificate."
            })

        return self.findings
