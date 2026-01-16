# Data Collection Guide

## Overview

This document details the complete workflow for collecting, processing, and extracting URLs from academic journal articles. The project focuses on two main journals:

1. **European Contemporary History** (Cambridge University Press)
2. **Journal of Contemporary History** (SAGE Publications)

Each journal collection follows a similar pipeline but uses different access methods and scripts tailored to the publisher's website structure.

## Collection Pipeline

The data collection process follows these four main stages:

```
1. DOI/Article Discovery
   ↓
2. PDF Download
   ↓
3. Text Extraction
   ↓
4. URL Extraction & Analysis
```

## Journal of Contemporary History (SAGE)

### Source Information
- **Publisher:** SAGE Publications
- **Access Method:** Library proxy

### Stage 1: DOI Extraction

**Purpose:** Scrapes SAGE journal search results to extract Digital Object Identifiers (DOIs) for all articles matching specific search queries.

**Key Features:**
- Handles pagination automatically
- Extracts DOIs using regex patterns from article links
- Captures article titles alongside DOIs

**Technology Stack:**
- Selenium WebDriver
- BeautifulSoup for HTML parsing
- Regex for DOI pattern matching



**Search Queries:**
The extraction was configured to search for articles related to specific topics. In this case "internet" and "web".

### Stage 2: PDF Download

**Purpose:** Downloads PDF files for each extracted DOI through the library proxy system.

**Key Features:**
- Reads DOIs from stage 1
- Uses library proxy 
- Tracks download progress and handles failures

### Stage 3: Text Extraction

**Script:** `extract_full_pdf_text_sage.py`

**Purpose:** Extracts complete text content from downloaded PDFs, including body text, footnotes, citations, and references.

**Key Features:**
- Uses `pdfplumber` library for comprehensive text extraction
- Captures all text elements including footnotes
- Preserves page boundaries with separators

**Technology:**
- `pdfplumber` - Superior footnote and layout handling
- Page-by-page processing with progress indicators

**Output Format:**
```
================================================================================
PAGE 1
================================================================================

[Full text content including footnotes]

================================================================================
PAGE 2
================================================================================

[Continues for all pages...]
```

**Usage:**
```bash
cd journal_of_contemporary_history_sage
python ../scripts/batch_extract_pdfs.py --input-dir ./web/pdfs --output-dir ./web/texts
python ../scripts/batch_extract_pdfs.py --input-dir ./internet/pdfs --output-dir ./internet/texts
```

### Stage 4: URL Extraction

**Script:** `extract_urls_from_dir.py`

**Purpose:** Scans extracted text files to find and catalog all URLs referenced in the articles.

**Two Extraction Modes:**

1. **Strict Mode (default):**
   - Requires explicit URL schemes: `http://`, `https://`, or `www.`
   - More conservative, fewer false positives
   - Output: `urls.json`

2. **Lenient Mode (`-lenient` flag):**
   - Matches URLs without explicit schemes (e.g., `example.com`)
   - Catches more domain references
   - Output: `lenient_urls.json`

**Usage:**
```bash
# Strict extraction
python scripts/extract_urls_from_dir.py ./journal_of_contemporary_history_sage/web/texts \
  ./journal_of_contemporary_history_sage/web/urls.json

# Lenient extraction
python scripts/extract_urls_from_dir.py ./journal_of_contemporary_history_sage/web/texts \
  ./journal_of_contemporary_history_sage/web/lenient_urls.json -lenient
```

**Output Format:**
```json
[
  {
    "url": "https://example.com/article",
    "file": "./journal_of_contemporary_history_sage/web/texts/article-title.txt"
  },
  {
    "url": "http://doi.org/10.1234/example",
    "file": "./journal_of_contemporary_history_sage/web/texts/another-article.txt"
  }
]
```

## European Contemporary History (Cambridge)

### Source Information
- **Publisher:** Cambridge University Press
- **Journal:** Contemporary European History

### Stage 1: Article Discovery and PDF Download

**Purpose:** Discover articles from Cambridge search results and downloads PDFs in a single process.

**Key Features:**
- Searches Cambridge Core for specific query terms
- Extracts article page links from search results
- Navigates to each article page
- Identifies and downloads PDF links
- Sanitizes filenames for safe storage

**URL Pattern Recognition:**
- Article pages: `/core/journals/contemporary-european-history/article/`
- PDF service: `/core/services/aop-cambridge-core/content/view/`


### Stage 2: Text Extraction

**Script:** `batch_extract_pdfs.py` (same as SAGE)

**Usage:**
```bash
python scripts/batch_extract_pdfs.py --input-dir ./european_contemporary_history/web/pdfs \
  --output-dir ./european_contemporary_history/web/texts

python scripts/batch_extract_pdfs.py --input-dir ./european_contemporary_history/internet/pdfs \
  --output-dir ./european_contemporary_history/internet/texts
```

**Features:**
- Batch processes all PDFs in a directory
- Creates `.txt` files with same basename as source PDFs
- Reports success/failure statistics
- Shows character and line counts

### Stage 4: URL Extraction

**Same process as SAGE (see above)**

**Usage:**
```bash
# Strict URLs
python scripts/extract_urls_from_dir.py ./european_contemporary_history/web/texts \
  ./european_contemporary_history/web/urls.json

# Lenient URLs
python scripts/extract_urls_from_dir.py ./european_contemporary_history/web/texts \
  ./european_contemporary_history/web/lenient_urls.json -lenient
```



## Data Organization

### Directory Structure

```
DOI-extractor/
├── european_contemporary_history/
│   ├── web/
│   │   ├── pdfs/              # Downloaded PDF files (web search)
│   │   ├── texts/             # Extracted text files
│   │   ├── urls.json          # Strict URL extraction results
│   │   └── lenient_urls.json  # Lenient URL extraction results
│   └── internet/
│       ├── pdfs/              # Downloaded PDF files (internet search)
│       ├── texts/             # Extracted text files
│       ├── urls.json          # Strict URL extraction results
│       └── lenient_urls.json  # Lenient URL extraction results
│
├── journal_of_contemporary_history_sage/
│   ├── web/
│   │   ├── dois.json          # Extracted DOIs
│   │   ├── pdfs/              # Downloaded PDF files
│   │   ├── texts/             # Extracted text files
│   │   ├── urls.json          # Strict URL extraction results
│   │   └── lenient_urls.json  # Lenient URL extraction results
│   └── internet/
│       ├── dois.json
│       ├── pdfs/
│       ├── texts/
│       ├── urls.json
│       └── lenient_urls.json
│
├── scripts/
│   ├── batch_extract_pdfs.py      # Universal PDF-to-text extraction
│   ├── extract_urls_from_dir.py   # Universal URL extraction
│   ├── combine_json.py            # Combine multiple JSON files
│   ├── search_urls.py             # Search through URL collections
│   └── count_json_items.py        # Count items in JSON files
└── requirements.txt
```


## Post-Processing

### Combining URL Collections

After extracting URLs from multiple sources, combine them into a single dataset:

```bash
# Combine all lenient URLs from all sources
python scripts/combine_json.py \
  european_contemporary_history/web/lenient_urls.json \
  european_contemporary_history/internet/lenient_urls.json \
  journal_of_contemporary_history_sage/web/lenient_urls.json \
  journal_of_contemporary_history_sage/internet/lenient_urls.json \
  -o combined_lenient_urls.json

# Combine all strict URLs
python scripts/combine_json.py \
  european_contemporary_history/web/urls.json \
  european_contemporary_history/internet/urls.json \
  journal_of_contemporary_history_sage/web/urls.json \
  journal_of_contemporary_history_sage/internet/urls.json \
  -o combined_urls.json
```

### Counting and Statistics

```bash
# Count total URLs collected
python scripts/count_json_items.py combined_urls.json --detailed
python scripts/count_json_items.py combined_lenient_urls.json --detailed

# Count URLs per source
python scripts/count_json_items.py \
  european_contemporary_history/web/urls.json \
  european_contemporary_history/internet/urls.json \
  journal_of_contemporary_history_sage/web/urls.json \
  journal_of_contemporary_history_sage/internet/urls.json \
  --detailed
```

### Searching URL Collections

```bash
# Find all DOI references
python scripts/search_urls.py combined_urls.json "doi.org" -o doi_urls.json

# Find specific domains
python scripts/search_urls.py combined_urls.json "archive.org" -o archive_urls.json
python scripts/search_urls.py combined_urls.json "cambridge.org" --case-sensitive

# Search in file paths too
python scripts/search_urls.py combined_urls.json "spanish-civil-war" \
  --search-files -o spanish_war_urls.json
```


## Technical Requirements

### Python Dependencies

```txt
pdfplumber          # PDF text extraction
undetected-chromedriver  # Bot detection bypass
selenium            # Web automation
beautifulsoup4      # HTML parsing
requests            # HTTP library
```

Install all dependencies:
```bash
pip install -r requirements.txt
```


### System Requirements

- **Python:** 3.7+


## Troubleshooting

### Text Extraction Problems

If footnotes are missing:
- Verify using `pdfplumber` (not PyPDF2 or other libraries)
- Try layout-preserved mode: `extract_text(layout=True)`
- Check PDF is not image-based (requires OCR)

### URL Extraction Considerations

**Lenient mode caveats:**
- May capture false positives (e.g., `doi.10` without proper URL)
- Good for comprehensive discovery
- Use strict mode for cleaner, validated URLs

**Strict mode limitations:**
- Misses URLs without explicit schemes
- May miss domain-only references in academic text


## Data Collection Statistics

### Quality Metrics

**URL Extraction Quality:**
- Strict mode: Higher precision, lower recall
- Lenient mode: Higher recall, lower precision

**Text Extraction Completeness:**
- pdfplumber captures 95%+ of visible text
- Includes footnotes, headers, footers
- Page separators maintain document structure


## License and Ethics

### Access Considerations

- All downloads use institutional library access
- Respect robots.txt and rate limits
- Use undetected-chromedriver responsibly
- PDFs are for research purposes only

### Data Usage

- URLs extracted are public references
- PDF content subject to publisher copyrights
- Follow fair use guidelines for academic research
- Cite sources appropriately in publications


## References

### Key Libraries
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF text extraction
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) - Bot bypass
- [Selenium](https://www.selenium.dev/) - Web automation
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing

### Academic Sources
- Contemporary European History (Cambridge University Press)
- Journal of Contemporary History (SAGE Publications)
