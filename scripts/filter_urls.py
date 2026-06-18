#!/usr/bin/env python3
"""
Clean up a list of web links.

Links pulled straight out of PDF text often arrive slightly broken — with a
stray comma on the end, an "(accessed ...)" note glued on, or two links run
together. This tidies them up, and also drops two kinds of link that are not of
interest for the analysis: DOI links (which point to the articles themselves)
and Creative Commons licence links (which appear automatically on every article).

Run it like this:
    python scripts/filter_urls.py combined_urls.json filtered_urls.json
"""

import json
import sys
import os
import re

def filter_urls(input_path, output_path=None):
    """
    Filter out unwanted URLs from a JSON file containing URL entries.

    Removes entries with URLs matching:
    - doi.org (DOI resolver links)
    - creativecommons.org/licenses (Creative Commons license links)

    Entries without a 'url' key are also removed.

    Args:
        input_path (str): Path to the input JSON file. Expected to contain a list
                          of objects with at least a 'url' key.
        output_path (str, optional): Path to write the filtered JSON output.
                                     If not provided, defaults to the input path
                                     with '_filtered' appended before the extension.

    Returns:
        None. Writes the filtered list to the output file and prints a summary.

    Example:
        filter_urls('output/combined_urls.json', 'output/filtered_urls.json')
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    expanded = []
    for entry in data:
        url = entry['url']

        # Replace en-dashes with hyphens (common OCR/copy-paste artifact in URLs)
        url = url.replace('\u2013', '-').replace('\u2014', '-')

        # If multiple URLs are joined by ';', create a separate entry for each
        parts = [p.strip() for p in url.split(';') if p.strip()]
        if len(parts) > 1:
            for part in parts:
                expanded.append({**entry, 'url': part})
            continue
        expanded.append(entry)
    data = expanded

    for entry in data:
        url = entry['url']

        # Strip trailing punctuation
        url = url.rstrip('.,;:!?)>"\']')

        # Strip trailing citation text in many forms:
        #   (accessed ...), (lastaccessed ...), (last accessed ...),
        #   (lastvisited ...), (last visited ...), (lastaccessedon ...),
        #   ,accessed..., ,lastaccessed..., (documentnolongeravailable, etc.
        url = re.split(
            r'[\s;,]?\((?:last\s*accessed|lastaccessed|accessed|last\s*visited|lastvisited|lastaccessedon|document\s*no\s*longer)',
            url, flags=re.IGNORECASE
        )[0]

        # Also strip bare ",accessed" or ",lastaccessed" without parenthesis
        url = re.split(r',\s*(?:last\s*accessed|lastaccessed|accessed)', url, flags=re.IGNORECASE)[0]

        # Strip trailing punctuation again after cleaning
        url = url.rstrip('.,;:!?)>"\']')

        # Prepend scheme to bare www. URLs
        if url.startswith('www.'):
            url = 'http://' + url

        entry['url'] = url

    filtered = [
        entry for entry in data
        if 'doi.org' not in entry['url']
        and 'creativecommons.org/licenses' not in entry['url']
    ]

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_filtered{ext}"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)

    print(f"Original entries: {len(data)}")
    print(f"Filtered entries: {len(filtered)}")
    print(f"Removed: {len(data) - len(filtered)}")
    print(f"Output written to: {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python filter_urls.py <input.json> [output.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    filter_urls(input_file, output_file)