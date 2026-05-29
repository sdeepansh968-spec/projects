#!/usr/bin/env python3
"""
WebSentinel - Web Vulnerability Scanner
Author: [Your Name]
Description: A Python-based web vulnerability scanner that checks for common
             security misconfigurations and vulnerabilities in web applications.
"""

import argparse
import sys
import time
from datetime import datetime

from scanner.xss_scanner import XSSScanner
from scanner.sql_scanner import SQLiScanner
from scanner.header_scanner import HeaderScanner
from scanner.dir_scanner import DirectoryScanner
from reports.report_generator import ReportGenerator
from utils.logger import Logger

BANNER = """
 ██╗    ██╗███████╗██████╗ ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     
 ██║    ██║██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     
 ██║ █╗ ██║█████╗  ██████╔╝███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     
 ██║███╗██║██╔══╝  ██╔══██╗╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     
 ╚███╔███╔╝███████╗██████╔╝███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
  ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
                        Web Vulnerability Scanner v1.0
               For educational and authorized penetration testing ONLY
"""


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="WebSentinel - Web Vulnerability Scanner",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-u", "--url",
        required=True,
        help="Target URL to scan (e.g., http://testphp.vulnweb.com)"
    )
    parser.add_argument(
        "-s", "--scan",
        choices=["all", "xss", "sqli", "headers", "dirs"],
        default="all",
        help="Type of scan to run:\n"
             "  all     - Run all scans (default)\n"
             "  xss     - Cross-Site Scripting scan\n"
             "  sqli    - SQL Injection scan\n"
             "  headers - Security headers check\n"
             "  dirs    - Hidden directory enumeration"
    )
    parser.add_argument(
        "-o", "--output",
        help="Save report to file (e.g., report.txt)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)"
    )
    return parser.parse_args()


def run_scan(url, scan_type, timeout, verbose, logger):
    findings = []
    start_time = time.time()

    scanners = {
        "xss":     (XSSScanner,       "XSS Scanner"),
        "sqli":    (SQLiScanner,      "SQL Injection Scanner"),
        "headers": (HeaderScanner,    "Security Headers Scanner"),
        "dirs":    (DirectoryScanner, "Directory Enumeration"),
    }

    # Decide which modules to run
    if scan_type == "all":
        to_run = list(scanners.keys())
    else:
        to_run = [scan_type]

    for key in to_run:
        cls, label = scanners[key]
        logger.info(f"[*] Running {label}...")
        try:
            scanner = cls(url, timeout=timeout, verbose=verbose)
            results = scanner.scan()
            findings.extend(results)
            logger.success(f"[+] {label} complete — {len(results)} finding(s)")
        except Exception as e:
            logger.error(f"[-] {label} failed: {e}")

    elapsed = round(time.time() - start_time, 2)
    return findings, elapsed


def main():
    print(BANNER)
    args = parse_arguments()
    logger = Logger(verbose=args.verbose)

    logger.info(f"Target  : {args.url}")
    logger.info(f"Scan    : {args.scan}")
    logger.info(f"Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)

    # Run scans
    findings, elapsed = run_scan(
        url=args.url,
        scan_type=args.scan,
        timeout=args.timeout,
        verbose=args.verbose,
        logger=logger
    )

    print("-" * 70)

    # Generate and display report
    reporter = ReportGenerator(args.url, findings, elapsed)
    reporter.print_summary()

    if args.output:
        reporter.save_to_file(args.output)
        logger.success(f"[+] Report saved to: {args.output}")

    # Exit code: 1 if vulnerabilities found (useful in CI pipelines)
    sys.exit(1 if any(f["severity"] in ("HIGH", "CRITICAL") for f in findings) else 0)


if __name__ == "__main__":
    main()
