import os
import sys
from datetime import datetime, time
import json
from flask import current_app
from app import db
from app.models import User, ArticleBatch, SelectedArticle
import uuid

# Add the Script directory to Python path to import modules
script_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Script')
sys.path.append(script_dir)

from app.tagging import (
    preprocess_text, assign_specific_topics_enhanced, rank_specific_topic_articles,
    extract_features, perform_topic_modeling, assign_topics_and_relevance,
    rank_articles_by_relevance, aggregate_articles
)
from app.summarizer import summarize_article
from app.email_template import generate_email_content

def sanitize_for_json(obj):
    """Convert NumPy types to standard Python types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif hasattr(obj, 'dtype') and hasattr(obj, 'tolist'):  # NumPy arrays
        return obj.tolist()
    elif hasattr(obj, 'item'):  # NumPy scalar types
        return obj.item()  # This converts to a Python scalar
    else:
        return obj

def collect_and_process_articles():
    """
    Collect articles, tag them, and store in the database
    Returns the batch ID for the collected articles
    """
    # Scrape and aggregate articles
    articles = aggregate_articles()
    
    # Preprocess article content
    for article in articles:
        article['content'] = preprocess_text(f"{article['title']} {article['summary']}")
        article['id'] = str(uuid.uuid4())  # Assign a unique ID to each article

    # Tag articles using enhanced method
    articles = assign_specific_topics_enhanced(articles)
    ranked_specific_articles = rank_specific_topic_articles(articles)
    
    # Process general articles with topic modeling
    general_articles = articles.copy()
    X, vectorizer = extract_features(general_articles)
    lda, topic_keywords = perform_topic_modeling(X, vectorizer, n_topics=10)
    
    general_articles = assign_topics_and_relevance(general_articles, lda, X)
    general_articles = rank_articles_by_relevance(general_articles)
    
    # Prepare the data structure for JSON serialization
    article_data = {
        'specific_articles': {topic: [article for article in articles] 
                             for topic, articles in ranked_specific_articles.items()},
        'general_articles': [article for article in general_articles]
    }
    
    # Convert NumPy types to Python types before serialization
    sanitized_data = sanitize_for_json(article_data)
    
    # Store the processed articles in the database
    new_batch = ArticleBatch(
        date_created=datetime.now(),
        is_finalized=False,
        articles_json=json.dumps(sanitized_data)
    )
    db.session.add(new_batch)
    db.session.commit()
    
    return new_batch.id

def get_latest_batch():
    """
    Get the latest article batch from the database
    """
    return ArticleBatch.query.order_by(ArticleBatch.date_created.desc()).first()

def select_articles_automatically(batch_id=None):
    """
    Automatically select top articles from the latest batch
    """
    batch = ArticleBatch.query.get(batch_id) if batch_id else get_latest_batch()
    if not batch:
        raise Exception("No article batch found")
    
    articles_data = json.loads(batch.articles_json)
    specific_articles = articles_data.get('specific_articles', {})
    general_articles = articles_data.get('general_articles', [])
    
    # Select top articles from each category
    selected_articles = {}
    
    # Select 1-2 top articles from each specific topic
    for topic, articles in specific_articles.items():
        if articles:
            # Sort by rank
            sorted_articles = sorted(articles, key=lambda x: x.get('rank', 999))
            # Select top 1-2 articles per topic depending on topic importance
            num_to_select = 2 if topic in ['AI', 'Cybersecurity', 'Web Development'] else 1
            selected_articles[topic] = sorted_articles[:num_to_select]
    
    # Store selected articles
    batch.selected_json = json.dumps(selected_articles)
    batch.is_finalized = True
    db.session.commit()
    
    return selected_articles

def get_selected_articles(batch_id=None):
    """
    Get the selected articles from a batch
    """
    batch = ArticleBatch.query.get(batch_id) if batch_id else get_latest_batch()
    if not batch or not batch.selected_json:
        return None
    
    return json.loads(batch.selected_json)

def generate_preview_content(batch_id=None):
    """
    Generate preview content for the newsletter based on selected articles
    """
    selected_articles = get_selected_articles(batch_id)
    if not selected_articles:
        raise Exception("No selected articles found")
    
    # Summarize selected articles
    summarized_articles = {}
    for topic, articles in selected_articles.items():
        summarized_articles[topic] = [(article, summarize_article(article)) for article in articles]
    
    # Generate email content
    email_content = generate_email_content(summarized_articles)
    
    return email_content

def add_custom_article(batch_id, title, link, summary, topic):
    """
    Add a custom article to the selected articles
    """
    batch = ArticleBatch.query.get(batch_id)
    if not batch:
        raise Exception("Batch not found")
    
    # Create the custom article
    custom_article = {
        'title': title,
        'link': link,
        'summary': summary,
        'source': 'Custom',
        'specific_topic': topic,
        'custom': True
    }
    
    # Add to selected articles
    selected_articles = json.loads(batch.selected_json) if batch.selected_json else {}
    
    if topic not in selected_articles:
        selected_articles[topic] = []
    
    selected_articles[topic].append(custom_article)
    batch.selected_json = json.dumps(selected_articles)
    db.session.commit()
    
    return custom_article

def finalize_newsletter(batch_id=None):
    """
    Finalize the newsletter by generating the content and marking it as ready to send
    """
    batch = ArticleBatch.query.get(batch_id) if batch_id else get_latest_batch()
    if not batch:
        raise Exception("No article batch found")
    
    # If no articles have been selected yet, do automatic selection
    if not batch.selected_json:
        select_articles_automatically(batch.id)
        
    # Generate the email content
    email_content = generate_preview_content(batch.id)
    
    # Store the email content
    batch.email_content = email_content
    batch.is_finalized = True
    db.session.commit()
    
    return email_content