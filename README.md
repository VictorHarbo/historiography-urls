# URL Extraction and Management Tools

[![DOI](https://zenodo.org/badge/1135601642.svg)](https://doi.org/10.5281/zenodo.18267734)


A collection of Python scripts for extracting, combining, searching, and analyzing URLs from large text corpora.

## Installation

Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Core Scripts

### 1. Extract URLs from Text Files (`extract_urls_from_dir.py`)

Extracts URLs from all text files in a directory and saves them to a JSON file.

**Usage:**
```bash
python scripts/extract_urls_from_dir.py <input_directory> <output_file.json>
```

**Example:**
```bash
python scripts/extract_urls_from_dir.py ./texts ./urls.json
```

**Features:**
- Processes all `.txt` files in a directory
- Extracts URLs using regex patterns
- Supports both strict and lenient URL matching
- Saves results with source file information
- Handles large text corpora efficiently

**Output Format:**
```json
[
  {
    "url": "https://example.com/page",
    "file": "./texts/document1.txt"
  },
  {
    "url": "http://doi.org/10.1234/example",
    "file": "./texts/document2.txt"
  }
]
```

### 2. Combine JSON Files (`combine_json.py`)

Combines multiple JSON files into a single file with configurable merging strategies.

**Usage:**
```bash
python scripts/combine_json.py file1.json file2.json file3.json -o combined.json
python scripts/combine_json.py *.json --output result.json --indent 4
```

**Features:**
- Smart merging: concatenates lists, merges dictionaries
- Configurable output path and indentation
- Handles mixed data types
- Creates output directories automatically
- Error handling for invalid JSON

**Example:**
```bash
# Combine all lenient_urls.json files from different directories
python scripts/combine_json.py \
  european_contemporary_history/web/lenient_urls.json \
  european_contemporary_history/internet/lenient_urls.json \
  journal_of_contemporary_history_sage/internet/lenient_urls.json \
  -o combined_lenient_urls.json
```

### 3. Search URLs (`search_urls.py`)

Search through JSON URL lists to find URLs matching specific terms.

**Usage:**
```bash
python scripts/search_urls.py <input_file.json> <search_term> [options]
```

**Examples:**
```bash
# Find all DOI URLs
python scripts/search_urls.py combined_urls.json doi

# Case-sensitive search for Cambridge URLs
python scripts/search_urls.py combined_urls.json cambridge --case-sensitive

# Search in both URLs and file paths, save results
python scripts/search_urls.py combined_urls.json spain --search-files -o results.json
```

**Options:**
- `--case-sensitive`: Perform case-sensitive search
- `--search-files`: Also search in file path fields
- `--no-show-files`: Hide file paths in output
- `-o, --output`: Save results to JSON file
- `--indent`: Set JSON indentation level

### 4. Count JSON Items (`count_json_items.py`)

Count the number of items in JSON files (lists or dictionary keys).

**Usage:**
```bash
python scripts/count_json_items.py <file.json> [options]
python scripts/count_json_items.py *.json --detailed
```

**Features:**
- Works with JSON lists and objects
- Detailed analysis mode showing structure info
- Supports multiple files with totals
- Detects URL entries and data types

**Example:**
```bash
python scripts/count_json_items.py combined_urls.json --detailed
```

**Output:**
```
Count: 6842 list items
Type: list
Item type: objects (dictionaries)
Sample keys: url, file
Contains URL entries: Yes
```

## Workflow Example

Complete workflow for extracting and analyzing URLs from multiple text corpora:

```bash
# Step 1: Extract URLs from different text directories
python scripts/extract_urls_from_dir.py ./european_contemporary_history/web/texts \
  ./european_contemporary_history/web/urls.json

python scripts/extract_urls_from_dir.py ./journal_of_contemporary_history_sage/web/texts \
  ./journal_of_contemporary_history_sage/web/urls.json

# Step 2: Combine all URL files
python scripts/combine_json.py \
  ./european_contemporary_history/web/urls.json \
  ./journal_of_contemporary_history_sage/web/urls.json \
  -o combined_urls.json

# Step 3: Count total URLs
python scripts/count_json_items.py combined_urls.json --detailed

# Step 4: Search for specific URLs
python scripts/search_urls.py combined_urls.json "doi.org" -o doi_urls.json
python scripts/search_urls.py combined_urls.json "archive.org" -o archive_urls.json

# Step 5: Count results
python scripts/count_json_items.py doi_urls.json archive_urls.json
```

## Additional Tools

### PDF Extraction (`batch_extract_pdfs.py`)

Extract text content from PDF files for further URL extraction.

### DOI Extraction

Various scripts for extracting DOIs from academic sources:
- `journal_of_contemporary_history_sage/extract_dois_sage.py`
- Related download and extraction scripts per journal

## Project Structure

```
DOI-extractor/
├── scripts/
│   ├── extract_urls_from_dir.py      # Main URL extraction script
│   ├── combine_json.py                # Combine multiple JSON files
│   ├── search_urls.py                 # Search through URL lists
│   ├── count_json_items.py            # Count items in JSON files
│   └── batch_extract_pdfs.py          # Batch PDF text extraction
├── requirements.txt                   # Python dependencies
└── [journal_directories]/             # Journal-specific tools and data
```

## Common Use Cases

### Find all DOI URLs
```bash
python scripts/search_urls.py combined_urls.json "doi.org" -o dois.json
```

### Find URLs from a specific domain
```bash
python scripts/search_urls.py combined_urls.json "cambridge.org" --case-sensitive
```

### Combine and analyze multiple URL collections
```bash
python combine_json.py dir1/urls.json dir2/urls.json -o all_urls.json
python count_json_items.py all_urls.json --detailed
```

### Search in file paths
```bash
python search_urls.py combined_urls.json "spanish-civil-war" --search-files
```
