"""
Report Generator Module
Formats and outputs scan findings in a readable format.
"""

from datetime import datetime


SEVERITY_COLORS = {
    "CRITICAL": "\033[91m",   # Red
    "HIGH":     "\033[91m",   # Red
    "MEDIUM":   "\033[93m",   # Yellow
    "LOW":      "\033[94m",   # Blue
    "INFO":     "\033[96m",   # Cyan
}
RESET = "\033[0m"
BOLD  = "\033[1m"


class ReportGenerator:
    def __init__(self, url, findings, elapsed_time):
        self.url = url
        self.findings = findings
        self.elapsed = elapsed_time
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _severity_color(self, severity):
        return SEVERITY_COLORS.get(severity, "")

    def _count_by_severity(self):
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for f in self.findings:
            sev = f.get("severity", "INFO")
            counts[sev] = counts.get(sev, 0) + 1
        return counts

    def print_summary(self):
        """Print colored terminal report."""
        counts = self._count_by_severity()

        print(f"\n{BOLD}{'='*70}{RESET}")
        print(f"{BOLD}  SCAN RESULTS — WebSentinel{RESET}")
        print(f"{'='*70}")
        print(f"  Target  : {self.url}")
        print(f"  Time    : {self.timestamp}")
        print(f"  Elapsed : {self.elapsed}s")
        print(f"  Total   : {len(self.findings)} finding(s)")
        print(f"{'='*70}\n")

        if not self.findings:
            print(f"  \033[92m[✓] No vulnerabilities detected.\033[0m")
            print(f"  Note: This does NOT guarantee the site is secure.")
            print(f"        Manual testing is always recommended.\n")
            return

        # Summary bar
        print(f"  Severity Breakdown:")
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if counts[sev]:
                color = self._severity_color(sev)
                print(f"    {color}[{sev}]{RESET}  {counts[sev]}")
        print()

        # Detailed findings
        for i, finding in enumerate(self.findings, 1):
            sev   = finding.get("severity", "INFO")
            color = self._severity_color(sev)

            print(f"  {BOLD}[{i}] {finding['type']}{RESET}")
            print(f"  {color}Severity : {sev}{RESET}")
            print(f"  URL      : {finding.get('url', self.url)}")

            if "payload" in finding:
                print(f"  Payload  : {finding['payload']}")
            if "parameter" in finding:
                print(f"  Parameter: {finding['parameter']}")
            if "status_code" in finding:
                print(f"  Status   : {finding['status_code']} {finding.get('status_label','')}")
            if "header_value" in finding:
                print(f"  Value    : {finding['header_value']}")

            print(f"  {BOLD}Description:{RESET}")
            print(f"    {finding.get('description', 'N/A')}")
            print(f"  {BOLD}Recommendation:{RESET}")
            print(f"    {finding.get('recommendation', 'N/A')}")
            print()

        print(f"{'='*70}")
        print(f"  {BOLD}Disclaimer:{RESET} Use only on systems you own or have written")
        print(f"  authorization to test. Unauthorized scanning is illegal.")
        print(f"{'='*70}\n")

    def save_to_file(self, filepath):
        """Save plain-text report to file."""
        counts = self._count_by_severity()
        lines = []

        lines.append("=" * 70)
        lines.append("  WEBSENTINEL VULNERABILITY SCAN REPORT")
        lines.append("=" * 70)
        lines.append(f"  Target  : {self.url}")
        lines.append(f"  Time    : {self.timestamp}")
        lines.append(f"  Elapsed : {self.elapsed}s")
        lines.append(f"  Total   : {len(self.findings)} finding(s)")
        lines.append("=" * 70)
        lines.append("")

        if not self.findings:
            lines.append("  [✓] No vulnerabilities detected.")
        else:
            lines.append("  Severity Breakdown:")
            for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                if counts[sev]:
                    lines.append(f"    [{sev}] {counts[sev]}")
            lines.append("")

            for i, finding in enumerate(self.findings, 1):
                lines.append(f"  [{i}] {finding['type']}")
                lines.append(f"  Severity     : {finding.get('severity', 'INFO')}")
                lines.append(f"  URL          : {finding.get('url', self.url)}")
                if "payload" in finding:
                    lines.append(f"  Payload      : {finding['payload']}")
                if "parameter" in finding:
                    lines.append(f"  Parameter    : {finding['parameter']}")
                if "status_code" in finding:
                    lines.append(f"  Status Code  : {finding['status_code']}")
                lines.append(f"  Description  : {finding.get('description', 'N/A')}")
                lines.append(f"  Recommendation: {finding.get('recommendation', 'N/A')}")
                lines.append("")

        lines.append("=" * 70)
        lines.append("  Disclaimer: For authorized testing only.")
        lines.append("=" * 70)

        with open(filepath, "w") as f:
            f.write("\n".join(lines))
