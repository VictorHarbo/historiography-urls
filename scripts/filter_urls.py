import json
import sys
import os

def filter_urls(input_path, output_path=None):
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