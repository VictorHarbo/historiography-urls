#!/usr/bin/env python3
"""
Combine multiple JSON files into a single JSON file.

Supports two merging strategies:
- If all files contain lists, concatenates them into a single list
- If all files contain dicts, merges them into a single dict
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List


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


def combine_json_files(input_files: List[Path]) -> Any:
    """
    Combine multiple JSON files into a single data structure.
    
    - If all files contain lists, concatenates them
    - If all files contain dicts, merges them (later files override earlier ones)
    - Otherwise, creates a list of all data
    """
    if not input_files:
        print("Error: No input files provided", file=sys.stderr)
        sys.exit(1)
    
    data_list = [load_json_file(f) for f in input_files]
    
    # Check if all data are lists
    if all(isinstance(data, list) for data in data_list):
        combined = []
        for data in data_list:
            combined.extend(data)
        return combined
    
    # Check if all data are dicts
    elif all(isinstance(data, dict) for data in data_list):
        combined = {}
        for data in data_list:
            combined.update(data)
        return combined
    
    # Mixed types - return as a list
    else:
        print("Warning: Mixed data types detected. Combining as a list.", file=sys.stderr)
        return data_list


def save_json_file(data: Any, filepath: Path, indent: int = 2) -> None:
    """Save data to a JSON file."""
    try:
        # Create parent directory if it doesn't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        print(f"Successfully wrote combined JSON to: {filepath}")
    except Exception as e:
        print(f"Error writing to {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Combine multiple JSON files into a single JSON file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file1.json file2.json file3.json -o combined.json
  %(prog)s *.json --output result.json
  %(prog)s input/*.json -o output/merged.json --indent 4
        """
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        type=Path,
        help='Input JSON files to combine'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        required=True,
        help='Output JSON file path'
    )
    
    parser.add_argument(
        '--indent',
        type=int,
        default=2,
        help='JSON indentation level (default: 2)'
    )
    
    args = parser.parse_args()
    
    # Validate input files exist
    for input_file in args.input_files:
        if not input_file.exists():
            print(f"Error: Input file does not exist: {input_file}", file=sys.stderr)
            sys.exit(1)
    
    print(f"Combining {len(args.input_files)} JSON files...")
    
    # Combine the JSON files
    combined_data = combine_json_files(args.input_files)
    
    # Save the result
    save_json_file(combined_data, args.output, indent=args.indent)
    
    # Print summary
    if isinstance(combined_data, list):
        print(f"Combined {len(args.input_files)} files into a list with {len(combined_data)} items")
    elif isinstance(combined_data, dict):
        print(f"Combined {len(args.input_files)} files into a dict with {len(combined_data)} keys")


if __name__ == '__main__':
    main()
