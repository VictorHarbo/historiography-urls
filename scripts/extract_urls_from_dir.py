#!/usr/bin/env python3
"""URL Extractor from Text Files

This script scans a directory of .txt files and extracts URLs using either a
strict or lenient regex pattern. It supports two output formats:
1. Plain text file with one unique URL per line
2. JSON file with URL-to-file mappings showing which files contain each URL

Usage:
    python extract_urls_from_dir.py [input_dir] [output_file] [-lenient]

Examples:
    # Extract URLs using strict regex to default output
    python extract_urls_from_dir.py
    
    # Extract URLs from custom directory with lenient regex to JSON
    python extract_urls_from_dir.py texts/ urls.json -lenient
    
    # Extract URLs with strict regex to plain text
    python extract_urls_from_dir.py texts/ extracted_urls.txt
"""

import os
import re
import argparse
import json

# Default directory containing .txt files
INPUT_DIR = "texts"
# Output file for extracted URLs
OUTPUT_FILE = "extracted_urls.txt"

# Strict (more stringent) URL regex, split into named parts for clarity
# - `STRICT_SCHEME`: explicit scheme or leading 'www.'
# - `STRICT_BODY`: the remainder of the URL (stops at whitespace/quote/angle-bracket)
STRICT_SCHEME = r'(?:https?://|www\.)'
STRICT_BODY = r'[^\s"\'<>]+'

URL_REGEX = re.compile(STRICT_SCHEME + STRICT_BODY, re.IGNORECASE)


# Lenient (more permissive) URL regex, split into parts and toggled by `-leniet`
# - `LENIET_SCHEME`: optional scheme prefixes (http, www, ftp)
# - `LENIENT_DOMAIN`: permissive domain matcher (subdomains, hyphens, TLD)
# - `LENIENT_PATH`: optional path portion that excludes whitespace and common delimiters
LENIENT_SCHEME = r'(?:https?://|www\.|ftp://)?'
LENIENT_DOMAIN = r'[A-Za-z0-9.-]+\.[A-Za-z]{2,6}'
LENIENT_PATH = r'(?:/[^\s"\'<>]*)?'

LENIENT_URL_REGEX = re.compile(LENIENT_SCHEME + LENIENT_DOMAIN + LENIENT_PATH, re.IGNORECASE)


def extract_urls_from_directory(input_dir, output_file, use_lenient=False):
    """Extract URLs from all .txt files in a directory.
    
    Scans all .txt files in the specified directory and extracts URLs using
    either a strict or lenient regex pattern. The results are written to a
    file in either plain text or JSON format based on the output filename.
    
    Args:
        input_dir (str): Path to directory containing .txt files to scan
        output_file (str): Path to output file. If ends with '.json', outputs
                          JSON format with URL-to-file mappings. Otherwise,
                          outputs plain text with one unique URL per line.
        use_lenient (bool): If True, uses a more permissive regex that catches
                           URLs without explicit schemes (e.g., 'example.com').
                           If False (default), only matches URLs with 'http://',
                           'https://', or 'www.' prefixes.
    
    Returns:
        None. Results are written to the output file.
    
    Raises:
        OSError: If files cannot be read (logged but does not stop execution)
    """
    # Map each URL to the set of files it was found in
    occurrences = {}

    # Choose regex based on flag: lenient allows URLs without explicit schemes
    regex = LENIENT_URL_REGEX if use_lenient else URL_REGEX

    # Process all .txt files in the directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".txt"):
            file_path = os.path.join(input_dir, filename)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    found_urls = regex.findall(content)

                    # Track which files contain each URL
                    for u in found_urls:
                        occurrences.setdefault(u, set()).add(file_path)
            except OSError as e:
                print(f"Could not read {file_path}: {e}")

    # Write output based on file extension
    if output_file.lower().endswith(".json"):
        # JSON format: list of {url, file} objects for each occurrence
        data = []
        for url, files in occurrences.items():
            for f in sorted(files):
                data.append({"url": url, "file": f})

        with open(output_file, "w", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2)

        print(f"Extracted {len(data)} URL occurrences to {output_file}")
    else:
        # Plain text format: one unique URL per line (sorted alphabetically)
        with open(output_file, "w", encoding="utf-8") as out:
            for url in sorted(occurrences.keys()):
                out.write(url + "\n")

        print(f"Extracted {len(occurrences)} unique URLs to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract URLs from .txt files in a directory")
    parser.add_argument("input_dir", nargs="?", default=INPUT_DIR,
                        help=f"Directory containing .txt files (default: {INPUT_DIR})")
    parser.add_argument("output_file", nargs="?", default=OUTPUT_FILE,
                        help=f"Output file for extracted URLs (default: {OUTPUT_FILE})")
    parser.add_argument("-lenient", action="store_true",
                        help="Use a more lenient URL regex")

    args = parser.parse_args()

    extract_urls_from_directory(args.input_dir, args.output_file, use_lenient=args.lenient)
