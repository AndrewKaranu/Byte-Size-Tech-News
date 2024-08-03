import os
from datetime import datetime
from scraper import aggregate_articles
from tagging import (
    preprocess_text, assign_specific_topics, rank_specific_topic_articles,
    extract_features, perform_topic_modeling, assign_topics_and_relevance,
    rank_articles_by_relevance
)
from summarizer import summarize_article, translate_content
from email_template import generate_email_content
from email_sender import send_email
from article_selection import select_top_articles, manual_article_selection

def main():
    print("Starting the news digest process...")

    # Step 1: Aggregate articles
    articles = aggregate_articles()
    print(f"Total articles aggregated: {len(articles)}")

    # Step 2: Preprocess and tag articles
    for article in articles:
        article['content'] = preprocess_text(f"{article['title']} {article['summary']}")
    
    articles = assign_specific_topics(articles)
    ranked_specific_articles = rank_specific_topic_articles(articles)

    # Step 3: Handle general articles
    general_articles = [article for article in articles if article['specific_topic'] is None]
    X, vectorizer = extract_features(general_articles)
    lda, topic_keywords = perform_topic_modeling(X, vectorizer, n_topics=10)
    general_articles = assign_topics_and_relevance(general_articles, lda, X)
    general_articles = rank_articles_by_relevance(general_articles)

    # Step 4: Article selection
    manual_selection = input("Do you want to manually select articles for today's digest? (y/n): ").lower() == 'y'
    
    if manual_selection:
        selected_articles = manual_article_selection(ranked_specific_articles, general_articles)
    else:
        selected_articles = select_top_articles(ranked_specific_articles, general_articles)

    # Step 5: Summarize selected articles
    summarized_articles = {}
    for topic, articles in selected_articles.items():
        summarized_articles[topic] = [(article, summarize_article(article)) for article in articles]

    # Step 6: Generate email content
    email_content = generate_email_content(summarized_articles)

    # Step 7: Send emails (commented out for now)
    # send_emails(email_content)

    print("News digest process completed!")

    # Optional: Save the digest to a file
    save_digest = input("Do you want to save today's digest to a file? (y/n): ").lower() == 'y'
    if save_digest:
        filename = f"digest_{datetime.now().strftime('%Y%m%d')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(email_content)
        print(f"Digest saved to {filename}")

def send_emails(email_content):
    # This function would contain your email sending logic
    # For now, we'll just print a message
    print("Emails would be sent here.")

if __name__ == "__main__":
    main()