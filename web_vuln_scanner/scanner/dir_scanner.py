"""
Directory & Sensitive File Scanner Module
Discovers hidden directories and exposed sensitive files on web servers.
"""

import requests
from urllib.parse import urljoin
import concurrent.futures


# Common directories and sensitive files to check
WORDLIST = [
    # Admin panels
    "admin", "admin/", "administrator", "admin/login", "wp-admin",
    "phpmyadmin", "cpanel", "dashboard", "backend", "manage",
    # Config and sensitive files
    ".env", ".git", ".git/config", ".htaccess", ".htpasswd",
    "config.php", "config.py", "config.js", "settings.py",
    "web.config", "database.yml", "secrets.yml", ".DS_Store",
    # Backup files
    "backup", "backup.zip", "backup.tar.gz", "backup.sql",
    "db_backup.sql", "site_backup.zip", "old", "bak",
    # Common paths
    "login", "signup", "register", "logout", "api", "api/v1",
    "api/v2", "test", "dev", "staging", "debug", "console",
    "server-status", "server-info", "status",
    # Log files
    "logs", "log", "error.log", "access.log", "debug.log",
    # Documentation
    "robots.txt", "sitemap.xml", "swagger", "swagger-ui", "docs",
    "api-docs", "graphql",
    # Upload directories
    "uploads", "upload", "files", "images", "static", "media",
]

# Status codes that indicate the resource exists
INTERESTING_CODES = {
    200: ("EXISTS", "HIGH"),
    201: ("CREATED", "MEDIUM"),
    301: ("REDIRECT", "LOW"),
    302: ("REDIRECT", "LOW"),
    401: ("AUTH_REQUIRED", "MEDIUM"),   # Exists but needs auth — still interesting!
    403: ("FORBIDDEN", "MEDIUM"),        # Exists but blocked — note worthy
}


class DirectoryScanner:
    def __init__(self, url, timeout=10, verbose=False):
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WebSentinel-Scanner/1.0 (Security Research)"
        })
        self.findings = []

    def _check_path(self, path):
        """Check if a single path exists."""
        full_url = urljoin(self.url + "/", path)
        try:
            response = self.session.get(
                full_url,
                timeout=self.timeout,
                allow_redirects=False
            )
            if response.status_code in INTERESTING_CODES:
                status_label, severity = INTERESTING_CODES[response.status_code]

                # Upgrade severity for critical files
                critical_files = [".env", ".git", "config", "backup", ".htpasswd", "database"]
                if any(cf in path for cf in critical_files):
                    severity = "CRITICAL"

                if self.verbose:
                    print(f"    [{response.status_code}] {full_url}")

                return {
                    "type": f"Exposed Path: /{path}",
                    "severity": severity,
                    "url": full_url,
                    "status_code": response.status_code,
                    "status_label": status_label,
                    "description": (
                        f"Path '/{path}' returned HTTP {response.status_code} ({status_label}). "
                        f"{'This may expose sensitive data or admin functionality.' if severity in ('HIGH', 'CRITICAL') else 'Resource exists on server.'}"
                    ),
                    "recommendation": (
                        "Restrict access with authentication, remove if unnecessary, "
                        "or add IP whitelisting for admin paths."
                    )
                }
        except Exception:
            pass
        return None

    def scan(self):
        """Scan using thread pool for speed."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_path = {
                executor.submit(self._check_path, path): path
                for path in WORDLIST
            }
            for future in concurrent.futures.as_completed(future_to_path):
                result = future.result()
                if result:
                    self.findings.append(result)

        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        self.findings.sort(key=lambda x: severity_order.get(x["severity"], 4))
        return self.findings
