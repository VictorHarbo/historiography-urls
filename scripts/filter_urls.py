import json
import sys
import os

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