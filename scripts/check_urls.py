#!/usr/bin/env python3
"""
Check whether a list of web links still works — the link-rot analysis.

This visits every link in a list and records what happens: the page loads
normally (a "200" reply), the page is gone (the familiar "404 not found"), or
the link is broken in some other way (the site has disappeared, times out, and
so on). To finish in reasonable time it checks many links at once.

It then writes two things next to the report file:
  - a detailed Markdown report listing every link grouped by outcome, and
  - a small summary image (.png) showing the totals at a glance.

Run it like this:
    python scripts/check_urls.py filtered_urls.json report.md
"""

import json
import sys
import os
import re
import time
import threading
import requests
import matplotlib
matplotlib.use('Agg')  # non-interactive backend, safe for scripts
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urlparse

MAX_REDIRECTS = 25
REQUEST_TIMEOUT = 15
MAX_WORKERS = 20  # concurrent requests


def is_valid_url(url):
    try:
        result = urlparse(url)
        return result.scheme in ('http', 'https') and bool(result.netloc)
    except Exception:
        return False


def check_url(session, url):
    """
    Check a URL by sending a HEAD request (falling back to GET if the server
    rejects HEAD). Uses stream=True to avoid downloading the response body.
    Retries with SSL verification disabled on SSL errors, and once on timeout.
    Handles redirect loops by capping at MAX_REDIRECTS.
    """
    def _request(method, verify=True):
        response = session.request(
            method,
            url,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
            stream=True,
            verify=verify,
        )
        response.close()
        return response

    try:
        try:
            response = _request('HEAD')
        except requests.exceptions.SSLError:
            # Retry without SSL verification for sites with expired/self-signed certs
            response = _request('HEAD', verify=False)
        # Some servers return 405 or 501 for HEAD — fall back to GET
        if response.status_code in (405, 501):
            response = _request('GET')
        return {
            'url': url,
            'status': response.status_code,
            'ok': response.status_code == 200,
            'error': None,
        }
    except requests.exceptions.TooManyRedirects:
        return {
            'url': url,
            'status': None,
            'ok': False,
            'error': f'Too many redirects (>{MAX_REDIRECTS})',
        }
    except requests.exceptions.SSLError as e:
        return {
            'url': url,
            'status': None,
            'ok': False,
            'error': f'SSL error: {e}',
        }
    except requests.exceptions.ConnectionError as e:
        return {
            'url': url,
            'status': None,
            'ok': False,
            'error': f'Connection error: {e}',
        }
    except requests.exceptions.Timeout:
        # One retry with a longer timeout before giving up
        try:
            response = _request('GET')
            return {
                'url': url,
                'status': response.status_code,
                'ok': response.status_code == 200,
                'error': None,
            }
        except Exception:
            pass
        return {
            'url': url,
            'status': None,
            'ok': False,
            'error': f'Timed out after {REQUEST_TIMEOUT}s',
        }
    except Exception as e:
        return {
            'url': url,
            'status': None,
            'ok': False,
            'error': str(e),
        }


def save_summary_png(results, skipped, png_path):
    """
    Render the summary counts as a table and save it as a PNG image.

    Args:
        results (list): List of result dicts from check_url().
        skipped (int): Number of entries skipped as invalid URLs.
        png_path (str): Destination path for the PNG file.
    """
    total = len(results) + skipped
    ok_count = sum(1 for r in results if r['ok'])

    rows = [
        ['Total entries', str(total)],
        ['Skipped (invalid URL)', str(skipped)],
        ['Checked', str(len(results))],
        ['HTTP 200 (working)', str(ok_count)],
    ]

    fig, ax = plt.subplots(figsize=(6, 0.45 * len(rows) + 1.2))
    ax.axis('off')

    col_labels = ['Metric', 'Count']
    col_widths = [0.74, 0.26]

    table = ax.table(
        cellText=rows,
        colLabels=col_labels,
        cellLoc='left',
        loc='center',
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)

    # Style header row
    for col in range(len(col_labels)):
        cell = table[0, col]
        cell.set_facecolor('#2c3e50')
        cell.set_text_props(color='white', fontweight='bold')

    # Alternating row colours; highlight the HTTP 200 row green
    for row_idx, row in enumerate(rows, start=1):
        for col in range(2):
            cell = table[row_idx, col]
            if row[0].strip().startswith('HTTP 200'):
                cell.set_facecolor('#d5f5e3')
            elif row_idx % 2 == 0:
                cell.set_facecolor('#f2f3f4')
            else:
                cell.set_facecolor('#ffffff')

    # Apply column widths
    for col, width in enumerate(col_widths):
        for row_idx in range(len(rows) + 1):
            table[row_idx, col].set_width(width)

    plt.title(
        f"URL Check Summary  ·  {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        fontsize=12, fontweight='bold', pad=10,
    )
    plt.tight_layout()
    plt.savefig(png_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def build_report(results, input_path, skipped):
    total = len(results) + skipped
    ok = [r for r in results if r['ok']]

    # Group non-200 results by status code, then errors with no status
    by_status = {}
    errors = []
    for r in results:
        if r['ok']:
            continue
        if r['status'] is not None:
            by_status.setdefault(r['status'], []).append(r)
        else:
            errors.append(r)

    non_working_count = len(results) - len(ok)

    lines = [
        "# URL Check Report",
        "",
        f"**Input file:** `{input_path}`  ",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total entries | {total} |",
        f"| Skipped (invalid URL) | {skipped} |",
        f"| Checked | {len(results)} |",
        f"| ✅ HTTP 200 | {len(ok)} |",
        f"| ❌ Non-working | {non_working_count} |",
    ]
    for code in sorted(by_status):
        lines.append(f"| — HTTP {code} | {len(by_status[code])} |")
    lines.append("")

    if ok:
        lines += [f"## Working URLs — HTTP 200 ({len(ok)})", ""]
        for r in ok:
            lines.append(f"- `{r['url']}`")
        lines.append("")

    for code in sorted(by_status):
        group = by_status[code]
        lines += [
            f"## HTTP {code} ({len(group)})",
            "",
            "| URL | Source file |",
            "|-----|-------------|",
        ]
        for r in group:
            url_cell = r['url'].replace('|', '\\|')
            file_cell = r.get('file', '—').replace('|', '\\|')
            lines.append(f"| `{url_cell}` | {file_cell} |")
        lines.append("")

    return "\n".join(lines)


def main():
    """
    Entry point for the URL checker script.

    Reads a JSON file containing a list of URL entries, sends a GET request to
    each valid URL, and writes a Markdown report summarising the results.

    Command-line usage:
        python check_urls.py <input.json> [output_report.md]

    Arguments:
        input.json       Path to a JSON file containing a list of objects, each
                         with at least a 'url' key (string). Entries whose 'url'
                         value is not a well-formed http/https URL are skipped.
        output_report.md (optional) Path for the generated Markdown report.
                         Defaults to <input>_report.md in the same directory.

    Behaviour:
        - Each URL is requested with a GET, following up to MAX_REDIRECTS (25)
          redirects. URLs that exceed the redirect limit are treated as broken.
        - A short delay (DELAY_BETWEEN_REQUESTS) is inserted between requests
          to avoid overloading servers.
        - Progress is printed to stdout as each URL is checked.
        - The final Markdown report groups URLs into working (HTTP 200) and
          non-working, with status codes and error messages for failures.

    Example:
        python scripts/check_urls.py output/filtered_urls.json output/report.md
    """
    if len(sys.argv) < 2:
        print("Usage: python check_urls.py <input.json> [output_report.md]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(input_path)[0] + '_report.md'

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Each thread gets its own session to avoid sharing connection state
    thread_local = threading.local()

    def make_session():
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        s.max_redirects = MAX_REDIRECTS
        adapter = requests.adapters.HTTPAdapter(max_retries=1)
        s.mount('http://', adapter)
        s.mount('https://', adapter)
        return s

    def get_session():
        if not hasattr(thread_local, 'session'):
            thread_local.session = make_session()
        return thread_local.session

    def check_entry(args):
        i, entry = args
        url = entry.get('url', '').strip()
        if not is_valid_url(url):
            return i, None  # sentinel for skipped
        try:
            result = check_url(get_session(), url)
        except Exception as e:
            result = {'url': url, 'status': None, 'ok': False, 'error': f'Unexpected: {e}'}
        return i, result

    results = []
    skipped = 0
    total = len(data)
    print_lock = threading.Lock()

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(check_entry, (i, entry)): i
                       for i, entry in enumerate(data, 1)}
            for future in as_completed(futures):
                i, result = future.result()
                if result is None:
                    skipped += 1
                    url = data[i - 1].get('url', '')
                    with print_lock:
                        print(f"[{i}/{total}] SKIP  {url[:80]}")
                else:
                    results.append(result)
                    status_label = f"HTTP {result['status']}" if result['status'] else result['error']
                    flag = '✅' if result['ok'] else '❌'
                    with print_lock:
                        print(f"[{i}/{total}] {flag}  {status_label}  {result['url'][:80]}")
    except KeyboardInterrupt:
        print(f"\nInterrupted. Writing partial report…")

    report = build_report(results, input_path, skipped)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    png_path = os.path.splitext(output_path)[0] + '_summary.png'
    save_summary_png(results, skipped, png_path)

    ok_count = sum(1 for r in results if r['ok'])
    print(f"\nDone. {ok_count}/{len(results)} URLs working.")
    print(f"Report written to:   {output_path}")
    print(f"Summary PNG written: {png_path}")


if __name__ == '__main__':
    main()
