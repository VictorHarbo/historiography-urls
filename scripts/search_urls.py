#!/usr/bin/env python3
"""
Search a list of web links for a particular word or address.

Given a JSON list of links, this finds and prints every entry containing the
search term — for instance, every link that mentions a web archive such as
"web.archive.org". Optionally it can also search the names of the articles the
links came from.

Run it like this:
    python scripts/search_urls.py combined_urls.json web.archive.org
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any


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


def search_urls(data: List[Dict[str, str]], search_term: str, 
                case_sensitive: bool = False, 
                search_files: bool = False) -> List[Dict[str, str]]:
    """
    Search through URL entries and find matches.
    
    Args:
        data: List of dictionaries containing 'url' and optionally 'file' keys
        search_term: The term to search for
        case_sensitive: Whether to perform case-sensitive search
        search_files: Whether to also search in the 'file' field
    
    Returns:
        List of matching entries
    """
    if not isinstance(data, list):
        print("Error: JSON data must be a list of objects", file=sys.stderr)
        sys.exit(1)
    
    matches = []
    search_value = search_term if case_sensitive else search_term.lower()
    
    for entry in data:
        if not isinstance(entry, dict):
            continue
        
        url = entry.get('url', '')
        file_path = entry.get('file', '')
        
        # Prepare search fields
        url_search = url if case_sensitive else url.lower()
        file_search = file_path if case_sensitive else file_path.lower()
        
        # Check if search term is in URL
        if search_value in url_search:
            matches.append(entry)
        # Optionally check file field
        elif search_files and search_value in file_search:
            matches.append(entry)
    
    return matches


def save_results(matches: List[Dict[str, str]], output_file: Path, indent: int = 2) -> None:
    """Save matching results to a JSON file."""
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(matches, f, indent=indent, ensure_ascii=False)
        print(f"Results saved to: {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}", file=sys.stderr)
        sys.exit(1)


def print_results(matches: List[Dict[str, str]], show_files: bool = True) -> None:
    """Print matching results to stdout, grouped by file."""
    if not matches:
        print("No matches found.")
        return
    
    # Group matches by file
    from collections import defaultdict
    grouped = defaultdict(list)
    for entry in matches:
        file_path = entry.get('file', 'N/A')
        grouped[file_path].append(entry.get('url', 'N/A'))
    
    print(f"\nFound {len(matches)} matching URL(s) across {len(grouped)} file(s)\n")
    print("=" * 80)
    
    # Sort files for consistent output
    for file_path in sorted(grouped.keys()):
        urls = grouped[file_path]
        
        if show_files:
            print(f"\nFile: {file_path}")
            print(f"URLs found: {len(urls)}")
            print("-" * 80)
        
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
        
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Search through a JSON file containing URLs and find matches.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s combined_urls.json doi
  %(prog)s urls.json cambridge --case-sensitive
  %(prog)s urls.json spain --search-files -o results.json
  %(prog)s urls.json creativecommons --no-show-files
        """
    )
    
    parser.add_argument(
        'input_file',
        type=Path,
        help='Input JSON file containing URLs'
    )
    
    parser.add_argument(
        'search_term',
        help='Word or phrase to search for in URLs'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Save results to a JSON file (optional)'
    )
    
    parser.add_argument(
        '--case-sensitive',
        action='store_true',
        help='Perform case-sensitive search (default: case-insensitive)'
    )
    
    parser.add_argument(
        '--search-files',
        action='store_true',
        help='Also search in the file path field'
    )
    
    parser.add_argument(
        '--no-show-files',
        action='store_true',
        help='Do not display file paths in output'
    )
    
    parser.add_argument(
        '--indent',
        type=int,
        default=2,
        help='JSON indentation level when saving (default: 2)'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not args.input_file.exists():
        print(f"Error: Input file does not exist: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Load the JSON data
    data = load_json_file(args.input_file)
    
    # Search for matches
    matches = search_urls(
        data, 
        args.search_term, 
        case_sensitive=args.case_sensitive,
        search_files=args.search_files
    )
    
    # Display results
    print_results(matches, show_files=not args.no_show_files)
    
    # Save results if output file specified
    if args.output:
        save_results(matches, args.output, indent=args.indent)
    
    # Exit with appropriate code
    sys.exit(0 if matches else 1)


if __name__ == '__main__':
    main()
