from scraper import scrape_techcrunch_rss, scrape_verge_rss, scrape_cnet_rss, scrape_eurogamer_rss, scrape_techradar_rss, scrape_mashable_rss, scrape_gizmodo_rss
import re
import google.generativeai as genai
import nltk
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# Ensure necessary NLTK data is downloaded
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
from sklearn.cluster import KMeans

# Combine all articles into a single data set
def aggregate_articles():
    def add_content_field(articles):
        for article in articles:
            article['content'] = f"{article['title']} - {article['summary']}"
        return articles

    # Scrape articles from different sources
    techcrunch_articles = scrape_techcrunch_rss()
    verge_articles = scrape_verge_rss()
    cnet_articles = scrape_cnet_rss()
    eurogamer_articles = scrape_eurogamer_rss()
    techradar_articles = scrape_techradar_rss()
    mashable_articles = scrape_mashable_rss()
    gizmodo_articles = scrape_gizmodo_rss()

    # Combine all articles
    all_articles = []
    all_articles.extend(techcrunch_articles)
    all_articles.extend(verge_articles)
    all_articles.extend(cnet_articles)
    all_articles.extend(eurogamer_articles)
    all_articles.extend(techradar_articles)
    all_articles.extend(mashable_articles)
    all_articles.extend(gizmodo_articles)

    # Add content field to all articles
    all_articles_with_content = add_content_field(all_articles)

    return all_articles_with_content

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
        article['topic_relevance'] = topic_distributions[i].max()
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
            
SPECIFIC_TOPICS = {
    'AI': {'artificial intelligence': 2, 'machine learning': 2, 'deep learning': 2,'AI': 2, 'OPENAI': 2, 'neural network': 1.5},
    'Web Development': {'web development': 2, 'frontend': 1.5, 'backend': 1.5, 'javascript': 1, 'html': 1, 'css': 1, 'react': 1, 'angular': 1, 'vue': 1},
    'Cybersecurity': {'cybersecurity': 2, 'hacking': 1.5, 'malware': 1.5, 'ransomware': 1.5, 'firewall': 1, 'encryption': 1},
    'Mobile Tech': {'smartphone': 1.5, 'android': 1, 'ios': 1, 'mobile app': 2, 'tablet': 1},
    'Cloud Computing': {'cloud': 1, 'aws': 1.5, 'azure': 1.5, 'google cloud': 1.5, 'saas': 1, 'iaas': 1, 'paas': 1}
}

def assign_specific_topics(articles):
    for article in articles:
        article['specific_topic'] = None
        article['topic_relevance'] = 0
        content = f"{article['title']} {article['summary']}".lower()
        for topic, keywords in SPECIFIC_TOPICS.items():
            score = sum(weight for keyword, weight in keywords.items() if keyword in content)
            if score > article['topic_relevance']:
                article['specific_topic'] = topic
                article['topic_relevance'] = score
    return articles

def rank_specific_topic_articles(articles):
    topic_articles = {}
    for topic in SPECIFIC_TOPICS.keys():
        topic_articles[topic] = sorted(
            [a for a in articles if a['specific_topic'] == topic],
            key=lambda x: x['topic_relevance'],
            reverse=True
        )
        for rank, article in enumerate(topic_articles[topic], 1):
            article['rank'] = rank
    return topic_articles

def print_specific_topics(ranked_specific_articles):
    for topic, articles in ranked_specific_articles.items():
        print(f"\n{topic} ({len(articles)} articles):")
        for article in articles[:5]:  # Print top 5 articles per specific topic
            print(f"  Rank {article['rank']}: {article['title']} (Relevance: {article['topic_relevance']:.2f})")

def main():
    articles = aggregate_articles()
    for article in articles:
        article['content'] = preprocess_text(f"{article['title']} {article['summary']}")
    
    articles = assign_specific_topics(articles)
    ranked_specific_articles = rank_specific_topic_articles(articles)
    
    # Filter out articles that have been assigned to specific topics
    general_articles = [article for article in articles if article['specific_topic'] is None]
    
    X, vectorizer = extract_features(general_articles)
    lda, topic_keywords = perform_topic_modeling(X, vectorizer, n_topics=10)
    
    general_articles = assign_topics_and_relevance(general_articles, lda, X)
    general_articles = rank_articles_by_relevance(general_articles)
    
    print_topic_info(topic_keywords, general_articles)
    print_specific_topics(ranked_specific_articles)



if __name__ == "__main__":
    main()