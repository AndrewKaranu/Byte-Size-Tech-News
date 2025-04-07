import json
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
# from deep_translator import GoogleTranslator

# Load the API key from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    api_key = config.get('api_key')
    
# Configure the Gemini API (you'll need to set up your API key)
genai.configure(api_key=api_key)

def extractive_summarize(text, num_sentences=3):
    sentences = nltk.sent_tokenize(text)
    vectorizer = TfidfVectorizer()
    sentence_vectors = vectorizer.fit_transform(sentences)
    similarity_matrix = cosine_similarity(sentence_vectors)
    scores = similarity_matrix.sum(axis=1)
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    return " ".join([s for _, s in ranked_sentences[:num_sentences]])

def gemini_summarize(text):
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    prompt = f"Summarize the following article in a concise paragraph:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

def summarize_article(article):
    full_text = f"{article['title']} - {article['summary']}"
    extractive_summary = extractive_summarize(full_text)
    final_summary = gemini_summarize(extractive_summary)
    return final_summary

# def translate_content(content, target_language):
#     translator = GoogleTranslator(source='auto', target=target_language)
#     return translator.translate(content)