import requests


def fetch_articles_from_crossref(journal_issn, max_articles=10):
    """
    Fetches articles from the Crossref API for a given journal ISSN.

    Args:
        journal_issn (str): ISSN of the journal.
        max_articles (int): Maximum number of articles to retrieve.
    """
    works_url = f"https://api.crossref.org/journals/{journal_issn}/works"
    params = {
        'rows': max_articles,
        'select': 'DOI,title,issued,is-referenced-by-count',
        'sort': 'is-referenced-by-count',
        'order': 'desc'
    }
    response = requests.get(works_url, params=params)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch articles: {response.status_code}")    
    
    data = response.json()
    articles = data.get('message', {}).get('items', [])
    
    if not articles:
        return {"error": "No articles found for the given ISSN."}
    
    return articles
    

def filter_articles_published_after_2000(articles):
    """
    Filters articles published after the year 2000.

    Args:
        articles (list): List of article dictionaries.

    Returns:
        list: Filtered list of articles published after 2000.
    """
    filtered_articles = []
    for article in articles:
        issued = article.get('issued')
        if issued and 'date-parts' in issued:
            year = issued['date-parts'][0][0] if issued['date-parts'][0] else None
            if year and year > 1993:
                filtered_articles.append(article)
    
    if not filtered_articles:
        return {"error": "No articles found published after 2000."}
    
    return filtered_articles

def get_most_cited_article_in_journal(journal_issn, max_articles=10):
    """
    This function retrieves the most cited article in a journal using the Crossref API.

    Args:
        journal_issn (str): ISSN of the journal.
        max_articles (int): Maximum number of articles to check for citations.

    Returns:
        dict: Information about the most cited article.
    """
    # Step 1: Retrieve a list of articles from the journal
    articles = fetch_articles_from_crossref(journal_issn, max_articles)


    # Step 2: Filter articles published after 2000
    filtered_articles = filter_articles_published_after_2000(articles)

    # Step 3: Find the article with the highest citation count
    most_cited_article = max(filtered_articles, key=lambda x: x.get('is-referenced-by-count', 0))

    return most_cited_article

def print_article_info(article):
    """
    Helper function to print article information in a readable format.

    Args:
        article (dict): Article information dictionary.
    """
    if 'error' in article:
        print(article['error'])
        return

    doi = article.get('DOI', 'N/A')
    title = article.get('title', ['N/A'])[0]
    issued = article.get('issued', {}).get('date-parts', [[None]])[0][0]
    citations = article.get('is-referenced-by-count', 0)

    print(f"Title: {title}")
    print(f"Publication Year: {issued}")
    print(f"DOI: {doi}")
    print(f"Citation Count: {citations}")
    print("-" * 40)


def main():
    """
    Main function to retrieve most cited articles in contemporary history journals.
    
    This function retrieves most cited articles (published after 2000) 
    from two major contemporary history journals:
    - Journal of Contemporary History (JCH)
    - Contemporary European History (CEH)
    
    For each journal, both the online and print ISSNs are queried to ensure 
    comprehensive coverage of all publications.
    
    The results include the article DOI, title, publication date, and citation count
    for the most cited article in each journal variant.
    """
    # Journal ISSNs for the two major contemporary history journals
    journal_of_contemporary_history_online_issn = '1461-7250'
    journal_of_contemporary_history_print_issn = '0022-0094'
    contemporary_european_history_online_issn = '1469-2171'
    contemporary_european_history_print_issn = '0960-7773'

    # Retrieve the most cited article for each journal variant
    JCH_online_most_cited = get_most_cited_article_in_journal(journal_of_contemporary_history_online_issn)
    JCH_print_most_cited = get_most_cited_article_in_journal(journal_of_contemporary_history_print_issn)

    CEH_online_most_cited = get_most_cited_article_in_journal(contemporary_european_history_online_issn)
    CEH_print_most_cited = get_most_cited_article_in_journal(contemporary_european_history_print_issn)

    # Display results
    print("Results:\n")
    print("Journal of Contemporary History (Online):\n")
    print_article_info(JCH_online_most_cited)
    print("Journal of Contemporary History (Print):\n")
    print_article_info(JCH_print_most_cited)
    print("Contemporary European History (Online):\n")
    print_article_info(CEH_online_most_cited)
    print("Contemporary European History (Print):\n")
    print_article_info(CEH_print_most_cited)


if __name__ == "__main__":
    main()