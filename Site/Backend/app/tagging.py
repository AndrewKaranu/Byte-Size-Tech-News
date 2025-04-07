from app.scraper import scrape_techcrunch_rss, scrape_verge_rss, scrape_cnet_rss, scrape_eurogamer_rss, scrape_techradar_rss
from app.scraper import scrape_mashable_rss, scrape_gizmodo_rss, scrape_wsj_rss, scrape_medium_topics
import re
import google.generativeai as genai
import nltk
import json
import time
import random
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure necessary NLTK data is downloaded
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt_tab', quiet=True)
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
from sklearn.cluster import KMeans

# Initialize Gemini API
gemini_available = False
gemini_model = None
try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    google_api_key = config.get('api_key')
    
    if google_api_key:
        genai.configure(api_key=google_api_key)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')
        gemini_available = True
        print("Gemini API initialized successfully")
    else:
        print("Google API key not found in config")
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading config: {str(e)}")
    print("Gemini integration disabled - using keyword-based tagging only")

# Combine all articles into a single data set
def aggregate_articles():
    """
    Aggregate articles from multiple sources and add necessary fields
    Returns a list of articles with standardized fields
    """
    # Scrape articles from different sources
    techrunch_articles = scrape_techcrunch_rss()
    verge_articles = scrape_verge_rss()
    cnet_articles = scrape_cnet_rss()
    eurogamer_articles = scrape_eurogamer_rss()
    techradar_articles = scrape_techradar_rss()
    mashable_articles = scrape_mashable_rss()
    gizmodo_articles = scrape_gizmodo_rss()
    wsj_articles = scrape_wsj_rss()
    # medium_articles = scrape_medium_topics(num_articles_per_topic=3)  # New Medium scraper

    # Combine all articles with source tracking
    all_articles = []
    
    def standardize_article(article):
        """Ensure all articles have consistent field names"""
        # Make a copy to avoid modifying the original
        standardized = article.copy()
        
        # Ensure all articles have these fields
        if 'summary' not in standardized:
            if 'description' in standardized:
                standardized['summary'] = standardized['description']
            elif 'excerpt' in standardized:
                standardized['summary'] = standardized['excerpt']
            else:
                standardized['summary'] = 'No summary available'
        
        if 'published' not in standardized:
            if 'publish_date' in standardized:
                standardized['published'] = standardized['publish_date']
            elif 'publication_date' in standardized:
                standardized['published'] = standardized['publication_date']
            elif 'date' in standardized:
                standardized['published'] = standardized['date']
            else:
                standardized['published'] = 'No publication date'
        
        # Add content field that combines title and summary for analysis
        standardized['content'] = f"{standardized['title']} - {standardized['summary']}"
        
        # Ensure link field is consistent 
        if 'link' not in standardized and 'url' in standardized:
            standardized['link'] = standardized['url']
        
        return standardized

    # Process and add articles from each source
    for articles_list in [techrunch_articles, verge_articles, cnet_articles, eurogamer_articles, 
                         techradar_articles, mashable_articles, gizmodo_articles, wsj_articles,
                         ]:  
        for article in articles_list:
            all_articles.append(standardize_article(article))
    
    print(f"Aggregated {len(all_articles)} articles from {len(set(a.get('source', 'Unknown') for a in all_articles))} sources")
    
    return all_articles

# Data preprocessing
def preprocess_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords and lemmatize
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return ' '.join(tokens)

# Converting text into feature vectors
def extract_features(articles):
    texts = [article['content'] for article in articles]
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    X = vectorizer.fit_transform(texts)
    return X, vectorizer

def perform_topic_modeling(X, vectorizer, n_topics=10):
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)
    
    feature_names = vectorizer.get_feature_names_out()
    topic_keywords = {}
    for topic_idx, topic in enumerate(lda.components_):
        top_keywords = [feature_names[i] for i in topic.argsort()[:-10 - 1:-1]]
        topic_keywords[topic_idx] = top_keywords
    
    return lda, topic_keywords

def assign_topics_and_relevance(articles, lda, X):
    topic_distributions = lda.transform(X)
    for i, article in enumerate(articles):
        article['topic'] = topic_distributions[i].argmax()
        article['topic_relevance'] = float(topic_distributions[i].max())  # Convert to float
    return articles

def rank_articles_by_relevance(articles):
    for topic in set(article['topic'] for article in articles):
        topic_articles = [a for a in articles if a['topic'] == topic]
        topic_articles.sort(key=lambda x: x['topic_relevance'], reverse=True)
        for rank, article in enumerate(topic_articles, 1):
            article['rank'] = rank
    return articles

def print_topic_info(topic_keywords, articles):
    for topic, keywords in topic_keywords.items():
        print(f"\nTopic {topic}: {', '.join(keywords)}")
        topic_articles = [a for a in articles if a['topic'] == topic]
        topic_articles.sort(key=lambda x: x['rank'])
        for article in topic_articles[:5]:  # Print top 5 articles per topic
            print(f"  Rank {article['rank']}: {article['title']} (Relevance: {article['topic_relevance']:.2f})")
            
# Enhanced topic keywords with broader coverage
SPECIFIC_TOPICS = {
    'AI': {'artificial intelligence': 2, 'machine learning': 2, 'deep learning': 2, 'ai': 2, 'openai': 2, 
           'neural network': 1.5, 'large language model': 2, 'llm': 2, 'generative ai': 2, 'chatgpt': 2, 
           'gemini': 1.5, 'claude': 1.5, 'gpt-4': 1.5, 'prompt': 1, 'image generation': 1.5},
           
    'Web Development': {'web development': 2, 'frontend': 1.5, 'backend': 1.5, 'javascript': 1, 'html': 1, 
                        'css': 1, 'react': 1, 'angular': 1, 'vue': 1, 'node': 1, 'rest api': 1.5, 'web app': 1.5,
                        'typescript': 1, 'webpack': 1, 'vite': 1, 'nextjs': 1.5, 'tailwind': 1},
                        
    'Cybersecurity': {'cybersecurity': 2, 'hacking': 1.5, 'malware': 1.5, 'ransomware': 1.5, 'firewall': 1, 
                      'encryption': 1, 'vulnerability': 1.5, 'exploit': 1.5, 'breach': 1.5, 'phishing': 1.5,
                      'zero-day': 2, 'cve': 1.5, 'attack': 1, 'security': 1},
                      
    'Mobile Tech': {'smartphone': 1.5, 'android': 1, 'ios': 1, 'mobile app': 2, 'tablet': 1, 'iphone': 1.5, 
                    'samsung': 1, 'pixel': 1, 'mobile device': 1.5, 'app store': 1, 'google play': 1,
                    'mobile gaming': 1.5, 'wearable': 1.5, 'smartwatch': 1.5},
                    
    'Cloud Computing': {'cloud': 1, 'aws': 1.5, 'azure': 1.5, 'google cloud': 1.5, 'saas': 1, 'iaas': 1, 
                        'paas': 1, 'serverless': 1.5, 'kubernetes': 1.5, 'docker': 1.5, 'containers': 1,
                        'microservices': 1.5, 'devops': 1.5, 'cicd': 1.5},
                        
    'Design': {'design': 2, 'ui': 1.5, 'ux': 1.5, 'graphic design': 1, 'web design': 1, 'product design': 1, 
               'interface': 1, 'user experience': 1.5, 'figma': 1, 'sketch': 1, 'adobe': 1,
               'prototype': 1, 'wireframe': 1.5, 'typography': 1},
               
    'Hardware': {'hardware': 2, 'computer': 1.5, 'laptop': 1.5, 'processor': 1, 'gpu': 1, 'ram': 1, 
                'motherboard': 1, 'ssd': 1, 'cpu': 1, 'intel': 1, 'amd': 1, 'nvidia': 1, 'monitor': 1,
                'peripheral': 1, 'keyboard': 1, 'mouse': 1, 'chip': 1.5},
                
    'Gaming': {'gaming': 2, 'game': 1.5, 'console': 1.5, 'playstation': 1.5, 'xbox': 1.5, 'nintendo': 1.5, 
              'steam': 1, 'esports': 1.5, 'gamedev': 1.5, 'game engine': 1.5, 'unity': 1, 'unreal': 1,
              'vr gaming': 1.5, 'video game': 1.5}
}

# Gemini-based tagging functionality
def tag_article_with_gemini(article):
    """Tag an article using Google's Gemini API for contextual understanding"""
    if not gemini_available:
        return None, 0
    
    try:
        title = article['title']
        summary = article.get('summary', '')
        
        # Construct prompt for Gemini
        prompt = f"""Analyze this tech article and classify it into EXACTLY ONE of these categories: 
AI, Web Development, Cybersecurity, Mobile Tech, Cloud Computing, Design, Hardware, Gaming, or Other.
Also rate its relevance/importance to the tech community on a scale from 1-10.

Title: {title}
Summary: {summary}

Return your answer in this exact JSON format only:
{{"category": "CHOSEN_CATEGORY", "relevance_score": SCORE, "reason": "Brief explanation of why"}}
"""
        
        response = gemini_model.generate_content(prompt)
        result_text = response.text
        
        try:
            # Extract JSON from response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            json_str = result_text[json_start:json_end]
            
            result = json.loads(json_str)
            
            # Get category and relevance score
            category = result.get('category', 'Other')
            relevance = result.get('relevance_score', 5)
            
            # For categories that don't match our predefined ones, map to Other
            if category not in SPECIFIC_TOPICS and category != 'Other':
                print(f"Gemini returned non-standard category: {category}, mapping to Other")
                category = 'Other'
                
            return category, float(relevance)
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error parsing Gemini response: {str(e)}, response: {result_text}")
            return None, 0
            
    except Exception as e:
        print(f"Error with Gemini API: {str(e)}")
        return None, 0

def tag_with_gemini_batch(articles, batch_size=10):
    """Tag articles in batches using Gemini"""
    if not gemini_available:
        print("Gemini tagging not available, skipping...")
        return articles
    
    print(f"Starting Gemini tagging with batch size {batch_size}...")
    tagged_count = 0
    
    # Use thread pool for parallel processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i+batch_size]
            futures = []
            
            for article in batch:
                future = executor.submit(tag_article_with_gemini, article)
                futures.append((future, article))
            
            for future, article in futures:
                try:
                    category, relevance = future.result()
                    if category:
                        article['gemini_topic'] = category
                        article['gemini_relevance'] = relevance
                        tagged_count += 1
                except Exception as e:
                    print(f"Error in Gemini tagging: {str(e)}")
                    
            # Add a small delay between batches to avoid API rate limits
            time.sleep(2)
            print(f"Progress: {min(i + batch_size, len(articles))}/{len(articles)} articles processed")
    
    print(f"Gemini tagging complete. Successfully tagged {tagged_count} articles.")
    return articles

# Keyword-based tagging (your original approach)
def assign_specific_topics(articles):
    """Assign topics using keyword matching"""
    for article in articles:
        article['keyword_topic'] = None
        article['keyword_relevance'] = 0
        content = f"{article['title']} {article['summary']}".lower()
        
        for topic, keywords in SPECIFIC_TOPICS.items():
            score = sum(weight for keyword, weight in keywords.items() if keyword in content)
            if score > article['keyword_relevance']:
                article['keyword_topic'] = topic
                article['keyword_relevance'] = score
    
    print("Keyword-based tagging complete")
    return articles

# Enhanced tagging function that combines both approaches
def assign_specific_topics_enhanced(articles, use_gemini=True):
    """
    Assign specific topics to articles using both keyword matching and Gemini
    
    Parameters:
    - articles: List of article dictionaries
    - use_gemini: Whether to use Gemini for tagging (if available)
    
    Returns:
    - List of tagged articles
    """
    # First, tag articles with Gemini if enabled and available
    if use_gemini and gemini_available:
        articles = tag_with_gemini_batch(articles, batch_size=10)
    
    # Then, apply the traditional keyword-based tagging
    articles = assign_specific_topics(articles)
    
    # Now combine the approaches
    print("Merging tagging results...")
    for article in articles:
        # If Gemini tagging was successful and has high confidence, use it
        if 'gemini_topic' in article and article['gemini_topic'] and article['gemini_relevance'] >= 6:
            article['specific_topic'] = article['gemini_topic']
            # Scale the Gemini relevance (1-10) to match the keyword relevance scale
            article['topic_relevance'] = float(article['gemini_relevance'] / 2)  # Convert to float
            article['tagging_method'] = 'Gemini'
        else:
            # Otherwise fall back to keyword tagging
            article['specific_topic'] = article['keyword_topic']
            article['topic_relevance'] = float(article['keyword_relevance'])  # Convert to float
            article['tagging_method'] = 'Keyword'
        
        # If neither method produced a result, mark as "Other"
        if not article['specific_topic']:
            article['specific_topic'] = 'Other'
            article['topic_relevance'] = 0.5
            article['tagging_method'] = 'Default'
    
    return articles

def rank_specific_topic_articles(articles):
    """Rank articles within each topic category by relevance"""
    topic_articles = {}
    # Collect unique topics (including 'Other')
    all_topics = set(article['specific_topic'] for article in articles)
    
    for topic in all_topics:
        # Get articles for this topic
        topic_articles[topic] = sorted(
            [a for a in articles if a['specific_topic'] == topic],
            key=lambda x: x['topic_relevance'],
            reverse=True
        )
        # Assign ranks
        for rank, article in enumerate(topic_articles[topic], 1):
            article['rank'] = rank
    
    return topic_articles

def print_specific_topics(ranked_specific_articles):
    """Print topic categories and their top articles"""
    for topic, articles in ranked_specific_articles.items():
        print(f"\n{topic} ({len(articles)} articles):")
        for article in articles[:5]:  # Print top 5 articles per specific topic
            tagging_method = article.get('tagging_method', 'Unknown')
            print(f"  Rank {article['rank']}: {article['title']} (Relevance: {article['topic_relevance']:.2f}, Method: {tagging_method})")

def main():
    # Scrape and aggregate articles
    articles = aggregate_articles()
    print(f"Processing {len(articles)} articles...")
    
    # Preprocess article content
    for article in articles:
        article['content'] = preprocess_text(f"{article['title']} {article['summary']}")
    
    # Tag articles using enhanced method (combines keywords and Gemini)
    articles = assign_specific_topics_enhanced(articles, use_gemini=gemini_available)
    ranked_specific_articles = rank_specific_topic_articles(articles)
    
    # Print results
    print("\n=== ARTICLE TAGGING RESULTS ===")
    print_specific_topics(ranked_specific_articles)
    
    # Return the results for use in other parts of the application
    return articles, ranked_specific_articles

if __name__ == "__main__":
    main()