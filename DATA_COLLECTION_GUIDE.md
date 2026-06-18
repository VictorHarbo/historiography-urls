# Data Collection Guide

This document explains, step by step, how the data behind the article was
gathered and processed. It is written to be read alongside the
[README.md](README.md), which introduces the project and the individual tools.
If a term is unfamiliar, the README has a short glossary.

## Overview

The aim was to find every web link cited in two contemporary-history journals
and then check whether those links still work. The journals are:

1. **Journal of Contemporary History** — published by SAGE
2. **Contemporary European History** — published by Cambridge University Press

Each journal was handled with the same overall recipe, but the first steps
differ because each publisher's website is built differently and has to be
approached in its own way.

## The four stages

Whichever journal is being processed, the work moves through four stages:

```
1. Find the articles      (which articles match our search?)
        ↓
2. Download the PDFs       (fetch a copy of each article)
        ↓
3. Extract the text        (pull the words out of each PDF)
        ↓
4. Find and analyse links  (collect the web links and check them)
```

Stages 3 and 4 are identical for both journals and use the shared tools in the
[scripts/](scripts/) folder. Stages 1 and 2 use journal-specific scripts.

A note on terminology used below:

- A **DOI** is a permanent identifier for an academic article (for example
  `10.1177/0022009419834575`). Collecting the DOIs is a convenient way to get a
  complete list of which articles to download.
- **Web scraping** means having a program automatically read pages from a
  website, the way a person would by clicking through them — only much faster.
- Publishers' sites try to block automated access, so the download scripts use
  a tool (`undetected-chromedriver`) that drives a real Chrome browser to look
  like an ordinary visitor. This is why a browser window opens when the scripts
  run, and why you may occasionally have to solve a "are you a robot?" puzzle by
  hand.

---

## Journal of Contemporary History (SAGE)

- **Publisher:** SAGE Publications
- **How articles were reached:** through a university library subscription
- **Scripts:** in the `journal_of_contemporary_history_sage/` folder

The scripts for stage 1 and 2 are not publicly available as they require institutional credentials.

### Stage 1 — Find the articles (`extract_dois_sage.py`)

This script searches the SAGE website for articles matching a chosen word and
collects the DOI (the article identifier) of every result. It clicks through
every page of search results automatically and saves the list of DOIs.

Two searches were run, one for the word **"web"** and one for **"internet"**,
to capture articles likely to cite online sources. The results of each were
kept separately (in the `web/` and `internet/` sub-folders).

### Stage 2 — Download the PDFs (`download_pdfs_sage.py`)

Working from the list of DOIs, this script downloads a PDF of each article
through the library subscription. It downloads in batches and pauses between
articles so as not to overload the publisher's servers.

### Stage 3 — Extract the text (`extract_full_pdf_text_sage.py` / `batch_extract_pdfs.py`)

This turns each PDF into a plain-text file so its contents can be searched.
The shared [scripts/batch_extract_pdfs.py](scripts/batch_extract_pdfs.py) tool
does this for a whole folder at once. It deliberately captures **footnotes**,
because that is where most web links are cited.

```bash
python scripts/batch_extract_pdfs.py \
  --input journal_of_contemporary_history_sage/web/pdfs \
  --output journal_of_contemporary_history_sage/web/texts

python scripts/batch_extract_pdfs.py \
  --input journal_of_contemporary_history_sage/internet/pdfs \
  --output journal_of_contemporary_history_sage/internet/texts
```

Each text file is laid out page by page, with a separator marking where each
page begins:

```
================================================================================
PAGE 1
================================================================================

[the full text of page 1, including footnotes]

================================================================================
PAGE 2
================================================================================

[and so on for every page]
```

### Stage 4 — Find the links (`extract_urls_from_dir.py`)

This scans the text files and collects every web link, saving the result as a
JSON file. As explained in the README, there are two modes:

- **Strict** (default) — only clear web addresses (`http://`, `https://`,
  `www.`). Saved to `urls.json`.
- **Lenient** (`-lenient`) — also catches domain-like text without a clear
  prefix. Saved to `lenient_urls.json`.

```bash
# Strict
python scripts/extract_urls_from_dir.py \
  journal_of_contemporary_history_sage/web/texts \
  journal_of_contemporary_history_sage/web/urls.json

# Lenient
python scripts/extract_urls_from_dir.py \
  journal_of_contemporary_history_sage/web/texts \
  journal_of_contemporary_history_sage/web/lenient_urls.json -lenient
```

The saved file is a list pairing each link with the article it came from:

```json
[
  {
    "url": "https://example.com/article",
    "file": "journal_of_contemporary_history_sage/web/texts/article-title.txt"
  }
]
```

---

## Contemporary European History (Cambridge)

- **Publisher:** Cambridge University Press
- **Scripts:** in the `european_contemporary_history/` folder

### Stages 1 & 2 — Find and download in one step (`download_cambridge_pdfs.py`)

For Cambridge, finding articles and downloading them is done by a single
script. It searches Cambridge Core for a chosen word, opens each article in the
results, finds the "Save PDF" link, and downloads the file — moving through
every page of results automatically.

As with the other journal, separate searches were run for **"web"** and
**"internet"**, kept in separate folders. This is also not available as it requires institutional credits.

### Stage 3 — Extract the text

This uses the same shared tool as the other journal:

```bash
python scripts/batch_extract_pdfs.py \
  --input european_contemporary_history/web/pdfs \
  --output european_contemporary_history/web/texts

python scripts/batch_extract_pdfs.py \
  --input european_contemporary_history/internet/pdfs \
  --output european_contemporary_history/internet/texts
```

### Stage 4 — Find the links

Also identical to the other journal:

```bash
# Strict
python scripts/extract_urls_from_dir.py \
  european_contemporary_history/web/texts \
  european_contemporary_history/web/urls.json

# Lenient
python scripts/extract_urls_from_dir.py \
  european_contemporary_history/web/texts \
  european_contemporary_history/web/lenient_urls.json -lenient
```

---

## How the files are organised

```
historiography-urls/
├── european_contemporary_history/
│   ├── web/                       # results of the "web" search
│   │   ├── pdfs/                  # downloaded PDF articles
│   │   ├── texts/                 # the extracted plain text
│   │   ├── urls.json              # links found (strict mode)
│   │   └── lenient_urls.json      # links found (lenient mode)
│   └── internet/                  # results of the "internet" search (same layout)
│
├── journal_of_contemporary_history_sage/
│   ├── web/
│   │   ├── dois.json              # the article identifiers found in stage 1
│   │   ├── pdfs/
│   │   ├── texts/
│   │   ├── urls.json
│   │   └── lenient_urls.json
│   └── internet/                  # (same layout)
│
├── scripts/                       # shared tools (stages 3 and 4, plus analysis)
└── output/                        # combined link lists and the final report
```

## Bringing it all together (post-processing)

Once links have been extracted from all four folders (two journals × two
searches), they are merged, cleaned, and checked. These steps use the shared
tools and are described in the README; the commands below show the exact runs
used for the article.

### Merge the link lists

```bash
# Merge every lenient list into one
python scripts/combine_json.py \
  european_contemporary_history/web/lenient_urls.json \
  european_contemporary_history/internet/lenient_urls.json \
  journal_of_contemporary_history_sage/web/lenient_urls.json \
  journal_of_contemporary_history_sage/internet/lenient_urls.json \
  -o output/combined_lenient_urls.json

# Merge every strict list into one
python scripts/combine_json.py \
  european_contemporary_history/web/urls.json \
  european_contemporary_history/internet/urls.json \
  journal_of_contemporary_history_sage/web/urls.json \
  journal_of_contemporary_history_sage/internet/urls.json \
  -o output/combined_urls.json
```

### Clean the merged list

```bash
python scripts/filter_urls.py output/combined_urls.json output/filtered_urls.json
```

### Count the links

```bash
python scripts/count_json_items.py output/combined_urls.json --detailed
python scripts/count_json_items.py output/combined_lenient_urls.json --detailed
```

### Check which links still work

```bash
python scripts/check_urls.py output/filtered_urls.json output/filtered_urls_report.md
```

### Search the links

```bash
# Find references to particular web archives
python scripts/search_urls.py output/combined_urls.json web.archive.org
python scripts/search_urls.py output/combined_urls.json archive-it.org
```

The full list of searches run for the article is recorded in
[SEARCH_LOG.md](SEARCH_LOG.md).

## What you need to run the code

### Supporting libraries

The scripts rely on a handful of free Python libraries, listed in
[requirements.txt](requirements.txt):

| Library | What it is used for |
|---------|---------------------|
| `pdfplumber` | Pulling text (and footnotes) out of PDFs |
| `requests` | Visiting web links to check whether they work |
| `matplotlib` | Drawing the summary image for the link-check report |
| `undetected-chromedriver` | Driving a real Chrome browser to download articles |
| `selenium` | Controlling the browser step by step |
| `beautifulsoup4` / `lxml` | Reading the structure of web pages |

Install them all with:

```bash
pip install -r requirements.txt
```

### System requirements

- **Python 3.7 or newer.**
- For the download scripts only: the **Google Chrome** browser installed, plus
  access to the journals (here, through a university library subscription).

## Troubleshooting

### Footnotes are missing from the extracted text

- Make sure `pdfplumber` is being used (other PDF tools often drop footnotes).
- If a PDF is really a scanned image rather than digital text, no tool can read
  it without optical character recognition (OCR) first.

### Strict vs. lenient link extraction

- **Lenient mode** finds more, but some matches will not be real links (for
  example, a fragment like `doi.10` with no proper address).
- **Strict mode** is cleaner but will miss links written without `http` or
  `www.` in front.
- For the article, both were produced so the trade-off could be examined
  directly.

## Ethics and access

- Articles were downloaded through legitimate institutional library access.
- The scripts pause between requests to avoid overloading publishers' servers.
- The downloaded PDFs remain under the publishers' copyright and are **not**
  shared in this repository. The extracted links — which are public references —
  and the analysis built from them are what is shared here.
- See [LICENSE.md](LICENSE.md) for the licence covering the code.

## Sources and further reading

### Libraries used
- [pdfplumber](https://github.com/jsvine/pdfplumber) — PDF text extraction
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) — automated browsing
- [Selenium](https://www.selenium.dev/) — browser automation
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) — reading web-page structure

### Journals studied
- Journal of Contemporary History (SAGE Publications)
- Contemporary European History (Cambridge University Press)
