import csv
import time
from TrainingDataScraper import scrape_medium_topics, scrape_medium_article

def scrape_and_save_medium_articles(filename='medium_articles.csv', num_articles_per_topic=100):
    # Scrape Medium articles
    medium_articles = scrape_medium_topics(num_articles_per_topic=num_articles_per_topic)
    
    # Fetch full content for each article
    for article in medium_articles:
        try:
            full_content = scrape_medium_article(article['link'])
            article['full_content'] = full_content.get('content', 'Content not found')
        except Exception as e:
            print(f"Failed to fetch Medium content for {article['link']}: {e}")
            article['full_content'] = 'Content not found'
        time.sleep(1)  # To avoid hitting Medium's rate limits
    
    # Save articles to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'content', 'summary', 'source', 'url', 'specific_topic'])
        writer.writeheader()
        
        for i, article in enumerate(medium_articles):
            writer.writerow({
                'id': i,
                'title': article['title'],
                'content': article['full_content'],
                'summary': article['summary'],
                'source': article['source'],
                'url': article['link'],
                'specific_topic': ''  # This will be filled during labeling
            })

if __name__ == "__main__":
    scrape_and_save_medium_articles()