import json
import nltk
import time
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from flask import current_app

# Global variable to track API usage
_api_calls_made = 0
_last_reset_time = time.time()
_quota_exhausted = False

def reset_usage_tracking():
    """Reset API usage tracking"""
    global _api_calls_made, _last_reset_time, _quota_exhausted
    current_time = time.time()
    # Reset every hour
    if current_time - _last_reset_time > 3600:
        _api_calls_made = 0
        _last_reset_time = current_time
        _quota_exhausted = False

def get_api_key():
    """Get API key from Flask config"""
    try:
        return current_app.config.get('GOOGLE_API_KEY')
    except RuntimeError:
        # If not in Flask context, try to load from config.json
        import os
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                return config.get('GOOGLE_API_KEY')
        except FileNotFoundError:
            print("Warning: Could not load API key from config")
            return None

# Configure the Gemini API
api_key = get_api_key()
if api_key:
    genai.configure(api_key=api_key)

def extractive_summarize(text, num_sentences=3):
    """Extractive summarization using TF-IDF"""
    try:
        sentences = nltk.sent_tokenize(text)
        if len(sentences) <= num_sentences:
            return text
        
        vectorizer = TfidfVectorizer(stop_words='english')
        sentence_vectors = vectorizer.fit_transform(sentences)
        similarity_matrix = cosine_similarity(sentence_vectors)
        scores = similarity_matrix.sum(axis=1)
        ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
        return " ".join([s for _, s in ranked_sentences[:num_sentences]])
    except Exception as e:
        print(f"Error in extractive summarization: {e}")
        # Fallback: return first few sentences
        sentences = text.split('. ')
        return '. '.join(sentences[:num_sentences]) + '.'

def gemini_summarize_with_retry(text, max_retries=3):
    """Gemini summarization with retry logic and rate limit handling"""
    global _api_calls_made, _quota_exhausted
    
    reset_usage_tracking()
    
    # If quota is exhausted, don't try
    if _quota_exhausted:
        print("⚠️ Gemini quota exhausted, using extractive summary only")
        return None
    
    # Limit API calls per session
    if _api_calls_made >= 50:  # Conservative limit
        print("⚠️ Approaching API limits, using extractive summary only")
        _quota_exhausted = True
        return None
    
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
            prompt = f"Summarize the following article in a concise paragraph (max 100 words):\n\n{text}"
            
            # Add some jitter to avoid overwhelming the API
            if attempt > 0:
                delay = (2 ** attempt) + random.uniform(0, 1)
                print(f"⏳ Waiting {delay:.1f}s before retry {attempt + 1}")
                time.sleep(delay)
            
            response = model.generate_content(prompt)
            _api_calls_made += 1
            print(f"✅ Gemini API call successful (total: {_api_calls_made})")
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"⚠️ Gemini quota/rate limit hit on attempt {attempt + 1}")
                if "retry_delay" in error_msg:
                    # Extract retry delay if available
                    try:
                        import re
                        delay_match = re.search(r'seconds: (\d+)', error_msg)
                        if delay_match:
                            retry_delay = int(delay_match.group(1))
                            print(f"⏳ API suggested waiting {retry_delay}s")
                            if retry_delay <= 30:  # Only wait if reasonable
                                time.sleep(retry_delay)
                                continue
                    except:
                        pass
                
                # Mark quota as exhausted after first quota error
                _quota_exhausted = True
                print("❌ Marking Gemini quota as exhausted for this session")
                break
            else:
                print(f"❌ Gemini API error on attempt {attempt + 1}: {error_msg}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
    
    return None

def summarize_article(article):
    """Summarize an article using hybrid approach"""
    try:
        full_text = f"{article.get('title', '')} - {article.get('summary', '')}"
        
        # First, create an extractive summary
        extractive_summary = extractive_summarize(full_text, num_sentences=2)
        
        # Try to enhance with Gemini, but fallback to extractive if needed
        enhanced_summary = gemini_summarize_with_retry(extractive_summary)
        
        if enhanced_summary:
            return enhanced_summary
        else:
            print("📝 Using extractive summary as fallback")
            return extractive_summary
            
    except Exception as e:
        print(f"❌ Error summarizing article: {e}")
        # Ultimate fallback
        return article.get('summary', article.get('title', 'No summary available'))[:200] + "..."

# def translate_content(content, target_language):
#     translator = GoogleTranslator(source='auto', target=target_language)
#     return translator.translate(content)