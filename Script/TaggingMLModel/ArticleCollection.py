import csv
import requests
from bs4 import BeautifulSoup
from TrainingDataScraper import (
    scrape_techcrunch_rss, scrape_verge_rss, scrape_cnet_rss, scrape_eurogamer_rss, 
    scrape_techradar_rss, scrape_mashable_rss, scrape_gizmodo_rss, scrape_wsj_rss,
    get_techcrunch_article, scrape_verge_article, scrape_cnet_article,
    scrape_eurogamer_article, scrape_techradar_article, scrape_mashable_article,
    scrape_gizmodo_article, scrape_medium_topic_page, scrape_medium_topics, scrape_medium_article
)
import logging
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a mapping between sources and their respective full article scraper functions
article_scrapers = {
    'TechCrunch': get_techcrunch_article,
    'The Verge': scrape_verge_article,
    'CNET': scrape_cnet_article,
    'Eurogamer': scrape_eurogamer_article,
    'TechRadar': scrape_techradar_article,
    'Mashable': scrape_mashable_article,
    'Gizmodo': scrape_gizmodo_article,
    'Medium': scrape_medium_article
}

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def validate_article(article):
    required_fields = ['title', 'link', 'summary', 'published', 'source']
    for field in required_fields:
        if field not in article or not article[field]:
            return False
    return True

def collect_articles_concurrently():
    all_articles = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(scrape_techcrunch_rss),
            executor.submit(scrape_verge_rss),
            executor.submit(scrape_cnet_rss),
            executor.submit(scrape_eurogamer_rss),
            executor.submit(scrape_techradar_rss),
            executor.submit(scrape_mashable_rss),
            executor.submit(scrape_gizmodo_rss),
            executor.submit(scrape_wsj_rss)
        ]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                articles = future.result()
                all_articles.extend(articles)
            except Exception as e:
                logging.error(f"Error collecting articles: {e}")
    
    # Collect Medium articles with proper content fetching
    medium_articles = scrape_medium_topics()
    for article in medium_articles:
        try:
            # Fetch full content immediately for Medium articles
            full_content = scrape_medium_article(article['link'])
            article['full_content'] = full_content.get('content', 'Content not found')
        except Exception as e:
            logging.error(f"Failed to fetch Medium content for {article['link']}: {e}")
            article['full_content'] = 'Content not found'
    
    all_articles.extend(medium_articles)
    
    # Validate and clean articles
    valid_articles = [article for article in all_articles if validate_article(article)]
    
    return valid_articles

def fetch_full_article_content(article):
    # For Medium articles, use the already fetched content
    if article['source'] == 'Medium' and 'full_content' in article:
        return article['full_content']
    
    # For other sources, use their respective scrapers
    scraper_function = article_scrapers.get(article['source'])
    if scraper_function:
        try:
            full_article = scraper_function(article['link'])
            return full_article.get('content', 'Content not found')
        except Exception as e:
            logging.error(f"Failed to fetch content for {article['link']}: {e}")
            return 'Content not found'
    else:
        return 'Content not found'

def create_unlabeled_csv(articles, filename='unlabeled_articles_2.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'content', 'summary', 'source', 'url', 'specific_topic'])
        writer.writeheader()
        
        for i, article in enumerate(articles):
            clean_content = clean_html(article['summary'])
            full_content = fetch_full_article_content(article)
            
            writer.writerow({
                'id': i,
                'title': article['title'],
                'content': full_content,
                'summary': clean_content,
                'source': article['source'],
                'url': article['link'],
                'specific_topic': ''  # This will be filled during labeling
            })

if __name__ == "__main__":
    articles = collect_articles_concurrently()
    create_unlabeled_csv(articles)
    logging.info(f"Created unlabeled_articles.csv with {len(articles)} articles.")