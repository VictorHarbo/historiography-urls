#!/usr/bin/env python3
"""
Count the number of items in a JSON file.

Works with both JSON lists and JSON objects (dictionaries).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json_file(filepath: Path) -> Any:
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def count_items(data: Any) -> int:
    """Count items in JSON data."""
    if isinstance(data, list):
        return len(data)
    elif isinstance(data, dict):
        return len(data)
    else:
        return 1


def analyze_json(data: Any) -> dict:
    """Analyze JSON structure and return statistics."""
    stats = {
        'type': type(data).__name__,
        'count': count_items(data)
    }
    
    if isinstance(data, list):
        stats['description'] = 'list items'
        if data:
            # Check if list contains objects with 'url' field
            first_item = data[0]
            if isinstance(first_item, dict):
                stats['item_type'] = 'objects (dictionaries)'
                if 'url' in first_item:
                    stats['has_urls'] = True
                # Count keys in first object as sample
                stats['sample_keys'] = list(first_item.keys())
    elif isinstance(data, dict):
        stats['description'] = 'dictionary keys'
        stats['keys'] = list(data.keys())
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Count the number of items in a JSON file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s combined_urls.json
  %(prog)s data.json --detailed
  %(prog)s *.json
        """
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        type=Path,
        help='Input JSON file(s) to count'
    )
    
    parser.add_argument(
        '-d', '--detailed',
        action='store_true',
        help='Show detailed information about the JSON structure'
    )
    
    args = parser.parse_args()
    
    total_count = 0
    
    for input_file in args.input_files:
        if not input_file.exists():
            print(f"Error: File does not exist: {input_file}", file=sys.stderr)
            continue
        
        # Load and count
        data = load_json_file(input_file)
        stats = analyze_json(data)
        
        # Display results
        if len(args.input_files) > 1:
            print(f"\n{input_file}:")
        
        print(f"  Count: {stats['count']} {stats.get('description', 'items')}")
        
        if args.detailed:
            print(f"  Type: {stats['type']}")
            if 'item_type' in stats:
                print(f"  Item type: {stats['item_type']}")
            if 'sample_keys' in stats:
                print(f"  Sample keys: {', '.join(stats['sample_keys'])}")
            if 'keys' in stats:
                print(f"  Keys: {', '.join(stats['keys'])}")
            if stats.get('has_urls'):
                print(f"  Contains URL entries: Yes")
        
        total_count += stats['count']
    
    # Show total if multiple files
    if len(args.input_files) > 1:
        print(f"\nTotal items across all files: {total_count}")


if __name__ == '__main__':
    main()
