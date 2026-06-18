# Search Log

This file records the searches run over the collected web links while
analysing the references for the article. It is kept as a record so the
analysis can be retraced.

Each line is a command run with the search tool
([scripts/search_urls.py](scripts/search_urls.py)): it looks through a list of
links and reports every one containing the given word. The words searched here
are the web addresses of well-known **web archives** (services that save copies
of web pages so they can be read after the original disappears) — the aim was
to find how often historians cite archived pages rather than live ones.

## Searches in `combined_urls.json`

These ran against the list of complete, clearly-formed links (strict mode).

1. `python search_urls.py ../output/combined_urls.json web.archive.org`
2. `python search_urls.py ../output/combined_urls.json webarchive.nationalarchives.gov.uk`
3. `python search_urls.py ../output/combined_urls.json arquivo.pt/wayback`
4. `python search_urls.py ../output/combined_urls.json arquivo.pt`
5. `python search_urls.py ../output/combined_urls.json nettarkivet.nb.no`
6. `python search_urls.py ../output/combined_urls.json archive-it.org`

## Searches in `combined_lenient_urls.json`

These ran against the fuller, lenient list. Because lenient mode is more
permissive, this file can contain matches that are not in fact real links, so
its results need to be read with more care.

1. `python search_urls.py ../output/combined_lenient_urls.json web.archive.org`
2. `python search_urls.py ../output/combined_lenient_urls.json webarchive.nationalarchives.gov.uk`
3. `python search_urls.py ../output/combined_lenient_urls.json arquivo.pt`
4. `python search_urls.py ../output/combined_lenient_urls.json nettarkivet.nb.no`
5. `python search_urls.py ../output/combined_lenient_urls.json archive-it.org`
