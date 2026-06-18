# Historiography URLs: Finding and Checking Web Links Cited in History Journals

[![DOI](https://zenodo.org/badge/1135601642.svg)](https://doi.org/10.5281/zenodo.18267734)

## What this project is

Historians increasingly cite material that lives on the web: digitised
archives, online newspapers, government reports, and pages saved in web
archives such as the [Wayback Machine](https://web.archive.org). This raises a
practical question — *how often do historians cite web pages, and do those
links still work years later?*

This repository contains the software that was written to answer that question
for an academic article. It does four things:

1. **Collects** articles from two contemporary-history journals (as PDF files).
2. **Reads** the text out of those PDFs.
3. **Finds** every web link (URL) mentioned in the text.
4. **Checks** whether each link still works today, and produces a report.

You do **not** need to run any of this software to read the article. The code
is published here for transparency, so that the analysis can be inspected and
reproduced. This README explains, in plain language, what each part does. A
companion document, [DATA_COLLECTION_GUIDE.md](DATA_COLLECTION_GUIDE.md),
walks through the full data-collection process step by step.

## A few terms explained

If you are not used to reading about software, these terms appear throughout:

| Term | What it means |
|------|---------------|
| **URL** | A web address, e.g. `https://web.archive.org`. Also called a "link". |
| **DOI** | *Digital Object Identifier* — a permanent code that identifies an academic article, e.g. `10.1177/0022009419834575`. Used to locate journal articles. |
| **PDF** | The file format most journal articles are downloaded in. |
| **JSON** | A plain-text file format used here to store lists of links. You can open these files in any text editor; they are human-readable. |
| **Script** | A small program. Each `.py` file in this project is one script that performs a single task. |
| **Run a script** | Type a command into a terminal (the Mac/Windows command-line) to make the program do its job. |

## The journals studied

- **Journal of Contemporary History** (published by SAGE)
- **Contemporary European History** (published by Cambridge University Press)

The files for each journal are kept in their own folder
(`journal_of_contemporary_history_sage/` and
`european_contemporary_history/`).

## Setting up (only needed if you want to run the code)

The scripts are written in [Python](https://www.python.org), a common
programming language. Once Python is installed, open a terminal in this folder
and install the supporting libraries the scripts rely on:

```bash
pip install -r requirements.txt
```

This reads the list in [requirements.txt](requirements.txt) and downloads each
library automatically.

## The tools, one by one

All of the general-purpose scripts live in the [scripts/](scripts/) folder.
They are designed to be run in sequence (see *A typical workflow* below), but
each can also be used on its own.

### 1. Read text out of PDFs — `batch_extract_pdfs.py`

Journal articles are downloaded as PDFs. Before any links can be found, the
text has to be pulled out of them. This script reads every PDF in a folder and
saves a plain-text (`.txt`) copy of each, footnotes included (footnotes are
where most web links are cited).

```bash
python scripts/batch_extract_pdfs.py --input pdfs --output texts
```

This reads PDFs from a folder called `pdfs` and writes the text files into a
folder called `texts`.

### 2. Find the web links — `extract_urls_from_dir.py`

This script scans a folder of text files and collects every web link it finds.
The result is saved as a JSON file: a list pairing each link with the article
it appeared in.

```bash
python scripts/extract_urls_from_dir.py texts urls.json
```

It has two modes for deciding what counts as a link:

- **Strict mode (default):** only counts text that clearly begins like a web
  address (`http://`, `https://`, or `www.`). Fewer mistakes, but may miss some
  links.
- **Lenient mode** (add `-lenient` at the end of the command): also counts
  things that merely *look* like a domain name (such as `example.com`). Catches
  more links, but also picks up some false matches that are not really links.

```bash
# Lenient mode
python scripts/extract_urls_from_dir.py texts lenient_urls.json -lenient
```

The two modes are used together: strict mode gives a clean list, lenient mode
gives a fuller one, and the difference between them can itself be informative.

### 3. Merge several lists into one — `combine_json.py`

Links are extracted journal-by-journal, producing several JSON files. This
script merges them into a single combined list so the whole corpus can be
analysed at once.

```bash
python scripts/combine_json.py file1.json file2.json -o combined.json
```

The `-o` (short for "output") names the file the merged list is written to.

### 4. Tidy up the list — `filter_urls.py`

Links pulled straight out of PDF text often arrive slightly broken — with a
stray comma stuck to the end, an "(accessed 3 May 2019)" note glued on, or two
links run together. This script cleans those up. It also removes two kinds of
link that are not of interest for the analysis: DOI links (which point to the
articles themselves) and Creative Commons licence links (which appear
automatically on every article).

```bash
python scripts/filter_urls.py combined_urls.json filtered_urls.json
```

### 5. Check whether the links still work — `check_urls.py`

This is the heart of the link-rot analysis. It visits every link in a list and
records what happens:

- The link works (the server replies "200", meaning "here is the page").
- The page is gone (a "404" reply, the familiar *page not found*).
- The link is broken in some other way (the site has disappeared, times out,
  and so on).

It then writes two things: a detailed report in Markdown
(`..._report.md`) listing every link grouped by outcome, and a small summary
image (`..._report_summary.png`) showing the totals at a glance.

```bash
python scripts/check_urls.py filtered_urls.json report.md
```

You can see a finished example in the [output/](output/) folder
([filtered_urls_report.md](output/filtered_urls_report.md)).

### 6. Search the list — `search_urls.py`

Once you have a list of links, you can search it for a particular word or web
address — for instance, to find every reference to a web archive.

```bash
# Find every link that mentions the Wayback Machine
python scripts/search_urls.py combined_urls.json web.archive.org
```

A record of the searches run for the article is kept in
[SEARCH_LOG.md](SEARCH_LOG.md).

### 7. Count the entries — `count_json_items.py`

A small helper that simply reports how many links are in a JSON file — useful
for checking totals.

```bash
python scripts/count_json_items.py combined_urls.json --detailed
```

## A typical workflow

The steps below show the whole process end to end, using the Journal of
Contemporary History as an example. The same steps work for either journal.

```bash
# Step 1 — turn the downloaded PDFs into text files
python scripts/batch_extract_pdfs.py \
  --input journal_of_contemporary_history_sage/web/pdfs \
  --output journal_of_contemporary_history_sage/web/texts

# Step 2 — find the web links in those text files
python scripts/extract_urls_from_dir.py \
  journal_of_contemporary_history_sage/web/texts \
  journal_of_contemporary_history_sage/web/urls.json

# Step 3 — merge the link lists from every folder into one
python scripts/combine_json.py \
  european_contemporary_history/web/urls.json \
  journal_of_contemporary_history_sage/web/urls.json \
  -o output/combined_urls.json

# Step 4 — clean up the merged list
python scripts/filter_urls.py output/combined_urls.json output/filtered_urls.json

# Step 5 — check which links still work and write the report
python scripts/check_urls.py output/filtered_urls.json output/filtered_urls_report.md

# Step 6 — (optional) search the list, e.g. for web-archive references
python scripts/search_urls.py output/combined_urls.json web.archive.org
```

## What is in each folder

```
historiography-urls/
├── README.md                  # This file
├── DATA_COLLECTION_GUIDE.md   # Step-by-step account of how the data was gathered
├── SEARCH_LOG.md              # Record of the searches run for the article
├── requirements.txt           # The supporting libraries the scripts need
│
├── scripts/                   # The general-purpose tools described above
│
├── output/                    # The combined link lists and the final report
│
├── journal_of_contemporary_history_sage/   # Files specific to this journal
└── european_contemporary_history/          # Files specific to this journal
```

The two journal folders each contain `web/` and `internet/` sub-folders. These
hold the results of two separate searches (for the words "web" and "internet")
within each journal, kept apart so they can be analysed individually or
together.

## A note on the gathering of articles

The scripts that download articles (in the two journal folders) rely on access
through a university library subscription, and the PDFs themselves are subject
to the publishers' copyright. They are not redistributed here. What *is* shared
is the list of web links extracted from the articles and the analysis built on
top of it. See [DATA_COLLECTION_GUIDE.md](DATA_COLLECTION_GUIDE.md) for the
details, and [LICENSE.md](LICENSE.md) for the licence terms.
