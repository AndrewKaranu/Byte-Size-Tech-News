import requests
from bs4 import BeautifulSoup
import feedparser
import re
import time
import random
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def make_request(url, max_retries=3):
    """Make HTTP request with retries but without proxies"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {str(e)}")
                raise
            delay = 2 * (attempt + 1) + random.uniform(0, 1)
            print(f"Request failed. Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

# RSS scrapers
def scrape_techcrunch_rss():
    feed_url = 'https://techcrunch.com/feed/'
    feed = feedparser.parse(feed_url)
    
    articles = []

    for entry in feed.entries[:20]:  # Limit to 20 articles
        article_data = {
            'title': entry.title or 'No title found',
            'link': entry.link or 'No link found',
            'summary': entry.summary or 'No summary available',
            'published': entry.published or 'No publication date found',
            'author': entry.get('author', 'Unknown'),
            'source': 'TechCrunch'
        }
        articles.append(article_data)

    return articles

def scrape_verge_rss():
    feed_url = 'https://www.theverge.com/rss/index.xml'
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries[:20]:  # Limit to 20 articles
        title = entry.title or 'No title found'
        link = entry.link or 'No link found'
        summary = entry.summary or 'No summary available'
        publication_date = entry.published or 'No publication date found'

        articles.append({
            'title': title,
            'link': link,
            'summary': summary,
            'published': publication_date,
            'source': 'The Verge'
        })
    
    return articles

def scrape_cnet_rss():
    url = "https://www.cnet.com/rss/tech/"
    feed = feedparser.parse(url)
    
    articles = []
    
    for entry in feed.entries[:20]:  # Limit to 20 articles
        article = {
            'title': entry.title or 'No title found',
            'summary': entry.summary or 'No summary available',
            'link': entry.link or 'No link found',
            'guide': entry.id or 'No guide found',
            'category': entry.get('category', 'N/A'),
            'published': entry.published or 'No publication date found',
            'thumbnail_url': entry.get('media_thumbnail', [{}])[0].get('url', 'No thumbnail') if entry.get('media_thumbnail') else 'No thumbnail',
            'content_url': entry.get('media_content', [{}])[0].get('url', 'No content') if entry.get('media_content') else 'No content',
            'creator': entry.get('dc_creator', 'Unknown'),
            'source': 'CNET'
        }
        articles.append(article)
    
    return articles

def scrape_eurogamer_rss():
    feed_url = "https://www.eurogamer.net/feed/blogs"
    feed = feedparser.parse(feed_url)

    articles = []

    for entry in feed.entries[:20]:  # Limit to 20 articles
        article = {
            'title': entry.title or 'No title found',
            'link': entry.link or 'No link found',
            'summary': entry.summary or 'No summary available',
            'published': entry.published or 'No publication date found',
            'source': 'Eurogamer'
        }
        articles.append(article)

    return articles

def scrape_techradar_rss():
    url = "https://www.techradar.com/feeds/articletype/news"
    feed = feedparser.parse(url)
    
    articles = []

    for entry in feed.entries[:20]:  # Limit to 20 articles
        article = {
            'title': entry.title or 'No title found',
            'link': entry.link or 'No link found',
            'summary': entry.summary or 'No summary available',
            'published': entry.published or 'No publication date found',
            'content': entry.get('dc_content', 'No content available'),
            'source': 'TechRadar'
        }
        articles.append(article)

    return articles

def scrape_mashable_rss():
    feed_url = 'https://mashable.com/feed'
    feed = feedparser.parse(feed_url)

    articles = []

    for entry in feed.entries[:20]:  # Limit to 20 articles
        articles.append({
            'title': entry.title or 'No title found',
            'link': entry.link or 'No link found',
            'summary': entry.summary or 'No summary available',
            'published': entry.published or 'No publication date found',
            'author': entry.get('author', 'Unknown'),
            'source': 'Mashable'
        })
    
    return articles

def scrape_gizmodo_rss():
    feed_url = 'https://gizmodo.com/rss'
    feed = feedparser.parse(feed_url)

    articles = []

    for entry in feed.entries[:20]:  # Limit to 20 articles
        articles.append({
            'title': entry.title or 'No title found',
            'link': entry.link or 'No link found',
            'summary': entry.summary or 'No summary available',
            'published': entry.published or 'No publication date found',
            'author': entry.get('author', 'Unknown'),
            'source': 'Gizmodo'
        })
    
    return articles

def scrape_wsj_rss():
    feed_url = 'https://feeds.content.dowjones.io/public/rss/RSSWSJD'
    feed = feedparser.parse(feed_url)
    
    articles = []

    for entry in feed.entries[:20]:  # Limit to 20 articles
        article = {
            'title': entry.get('title', 'No title found'),
            'link': entry.get('link', 'No link found'),
            'summary': entry.get('description', 'No description available'),
            'published': entry.get('published', 'No publication date found'),
            'author': entry.get('author', 'Unknown'),
            'source': 'Wall Street Journal'
        }
        articles.append(article)
    
    return articles

# Medium scraper functionality from TrainingDataScraper.py without proxies
def scrape_medium_topic_page(url, num_articles=10):
    """Scrape articles from a Medium topic page without using proxies"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        # Update this path to your chromedriver location
        service = Service(r'C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        articles = []
        last_height = driver.execute_script("return document.body.scrollHeight")

        while len(articles) < num_articles:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new articles to load

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # No more articles to load
            last_height = new_height

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            article_elements = soup.find_all('article')

            for article in article_elements:
                if len(articles) >= num_articles:
                    break

                # Skip member-only articles
                member_only_indicators = [
                    article.find('div', class_='mf ab'),
                    article.find('svg', {'aria-label': 'Member-only story'}),
                    article.find('button', {'aria-label': 'Member-only story'}),
                    article.find(string=lambda text: isinstance(text, str) and 'Member-only story' in text)
                ]

                is_member_only = any(member_only_indicators)
                if is_member_only:
                    continue

                title_element = article.find('h2')
                title = title_element.get_text(strip=True) if title_element else 'No title found'

                link_element = article.find('h2').parent if article.find('h2') else None
                if link_element and link_element.name == 'a' and link_element.get('href'):
                    href = link_element['href']
                    if href.startswith('/'):
                        link = f"https://medium.com{href}"
                    else:
                        link = href
                else:
                    link = 'No link found'

                summary_element = article.find('h3', class_='bf')
                summary = summary_element.get_text(strip=True) if summary_element else 'No summary found'

                articles.append({
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'source': 'Medium'
                })

        driver.quit()
        return articles
        
    except Exception as e:
        print(f"Error scraping Medium topic page: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return []

def scrape_medium_topics(num_articles_per_topic=5):
    """Scrape articles from multiple Medium topics with a lower article count"""
    topics = [
        'artificial-intelligence',
        'programming',
        'data-science',
        'technology',
        'cybersecurity'
    ]
    
    all_articles = []
    
    for topic in topics:
        try:
            url = f"https://medium.com/tag/{topic}/recommended"
            print(f"Scraping Medium topic: {topic}")
            articles = scrape_medium_topic_page(url, num_articles=num_articles_per_topic)
            all_articles.extend(articles)
            time.sleep(1)
        except Exception as e:
            print(f"Error scraping Medium topic {topic}: {str(e)}")
    
    return all_articles

def scrape_medium_article(url):
    """Scrape content from a Medium article without using proxies"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for content as Medium's structure can vary
        content_elements = []
        
        # Check for the main article section first
        article_section = soup.find('section', {'class': 'pw-post-body-container'})
        if article_section:
            content_elements = article_section.find_all(['p', 'h1', 'h2', 'h3', 'blockquote', 'pre'])
        
        # Fallback to other common content containers
        if not content_elements:
            content_elements = soup.find_all('p', class_='pw-post-body-paragraph')
        
        if not content_elements:
            content_elements = soup.find_all(['p', 'h1', 'h2', 'h3'], class_=lambda x: x and ('pw-' in x))
        
        # Filter out unwanted elements and join the text
        content = []
        for element in content_elements:
            # Skip elements that look like ads or promotions
            if element.find('a', string=re.compile(r'(>>.*Click here|Subscribe|Join Medium)')):
                continue
                
            # Skip elements that are likely navigation or UI elements
            if element.get('class') and any(c in ['nav', 'menu', 'header', 'footer'] for c in element.get('class')):
                continue
                
            text = element.get_text(strip=True)
            if text:
                content.append(text)
        
        full_content = ' '.join(content)
        
        # If content is too short, it might be paywalled or not properly scraped
        if len(full_content.split()) < 50:  # Arbitrary threshold for minimum article length
            return {'content': 'Content not found - Article may be paywalled or unavailable'}
            
        return {'content': full_content}
        
    except Exception as e:
        print(f"Error scraping Medium article {url}: {str(e)}")
        return {'content': f'Error fetching content: {str(e)}'}

# Article scrapers
def get_techcrunch_article(url):
    try:
        response = make_request(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('h1', class_='wp-block-post-title')
        title = title.get_text(strip=True) if title else 'No title found'

        subtitle = soup.find('h2', class_='wp-block-tc23-dek__heading')
        subtitle = subtitle.get_text(strip=True) if subtitle else 'No subtitle found'
        
        author_tag = soup.find('a', href=True, class_='wp-block-tc23-author-card-name')
        author = author_tag.get_text(strip=True) if author_tag else 'No author found'
        
        date_tag = soup.find('time')
        date = date_tag['datetime'] if date_tag and 'datetime' in date_tag.attrs else 'No date found'
        
        content_divs = soup.find_all('div', class_='wp-block-group')
        content = ' '.join([div.get_text(separator=' ', strip=True) for div in content_divs if div.find('p')]) if content_divs else 'Content not found'

        return {
            'title': title,
            'subtitle': subtitle,
            'author': author,
            'date': date,
            'content': content,
            'source': 'TechCrunch'
        }
    except Exception as e:
        print(f"Error scraping TechCrunch article: {str(e)}")
        return {'title': 'Error', 'content': f'Error: {str(e)}'}

def scrape_verge_article(url):
    try:
        response = make_request(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        title_tag = soup.find('h1', class_='mb-28 hidden max-w-[900px] font-polysans text-45 font-bold leading-100 selection:bg-franklin-20 lg:block')
        if not title_tag:
            title_tag = soup.find('h1', class_='inline font-polysans text-22 font-bold leading-110 md:text-33 lg:hidden')
        title = title_tag.get_text(strip=True) if title_tag else 'No title found'

        author_tag = soup.find('a', class_='hover:shadow-underline-inherit', href=lambda x: x and '/authors/' in x)
        author = author_tag.get_text(strip=True) if author_tag else 'No author found'

        date_tag = soup.find('time', class_='duet--article--timestamp')
        publish_date = date_tag['datetime'] if date_tag else 'No date found'

        content_div = soup.find('div', {'class': 'duet--article--article-body-component-container'})
        if content_div:
            paragraphs = content_div.find_all('p')
            content = ' '.join(paragraph.get_text() for paragraph in paragraphs)
        else:
            content = "Content not found"

        image_tag = soup.find('figure', class_='duet--article--lede-image w-full').find('img') if soup.find('figure', class_='duet--article--lede-image w-full') else None
        image_url = image_tag['src'] if image_tag else 'No image found'

        return {
            'title': title,
            'author': author,
            'publish_date': publish_date,
            'content': content,
            'image_url': image_url,
            'source': 'The Verge'
        }
    except Exception as e:
        print(f"Error scraping Verge article: {str(e)}")
        return {'title': 'Error', 'content': f'Error: {str(e)}'}

def scrape_cnet_article(url):
    try:
        response = make_request(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        title_tag = soup.find('h1', class_='c-contentHeader_headline')
        title = title_tag.get_text(strip=True) if title_tag else 'No title found'

        author_tag = soup.find('span', class_='c-globalAuthor_name')
        author = author_tag.get_text(strip=True) if author_tag else 'No author found'

        date_tag = soup.find('time', class_='c-globalAuthor_date')
        publish_date = date_tag.get_text(strip=True) if date_tag else 'No date found'

        content_div = soup.find('div', class_='c-pageArticle_content')
        if content_div:
            paragraphs = content_div.find_all('p')
            content = ' '.join(p.get_text(strip=True) for p in paragraphs)
        else:
            content = "Content not found"

        return {
            'title': title,
            'author': author,
            'publish_date': publish_date,
            'content': content,
            'source': 'CNET'
        }
    except Exception as e:
        print(f"Error scraping CNET article: {str(e)}")
        return {'title': 'Error', 'content': f'Error: {str(e)}'}

def scrape_eurogamer_article(article_url):
    try:
        response = make_request(article_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('h1', class_='title')
        title = title.get_text(strip=True) if title else 'No title found'

        strapline = soup.find('p', class_='strapline')
        strapline = strapline.get_text(strip=True) if strapline else 'No strapline found'

        author = soup.find('span', class_='author')
        author = author.get_text(strip=True) if author else 'No author found'

        publication_date = soup.find('time')
        publication_date = publication_date['datetime'] if publication_date else 'No date found'

        article_body = soup.find('div', class_='article_body_content')
        article_body = article_body.get_text(strip=True) if article_body else 'Content not found'

        return {
            'title': title,
            'strapline': strapline,
            'author': author,
            'publication_date': publication_date,
            'content': article_body,
            'source': 'Eurogamer'
        }
    except Exception as e:
        print(f"Error scraping Eurogamer article: {str(e)}")
        return {'title': 'Error', 'content': f'Error: {str(e)}'}

def scrape_techradar_article(url):
    try:
        response = make_request(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find title
        title = soup.find('h1')
        title = title.get_text(strip=True) if title else 'No title found'

        # Find author - look for author byline
        author_tag = soup.find('span', class_='author-byline__author-name')
        if author_tag:
            author = author_tag.find('a').get_text(strip=True) if author_tag.find('a') else 'No author found'
        else:
            author = 'No author found'

        # Find publish date
        date_tag = soup.find('time', class_='relative-date')
        publish_date = date_tag['datetime'] if date_tag else 'No date found'

        # Find article content - look for article-body div and all its paragraphs
        content_div = soup.find('div', id='article-body')
        if content_div:
            # Get all paragraphs but filter out ads and other unwanted content
            paragraphs = []
            for p in content_div.find_all('p'):
                # Skip if it's an ad unit
                if p.find_parent(class_='ad-unit'):
                    continue
                # Skip if paragraph is empty
                if not p.get_text(strip=True):
                    continue
                paragraphs.append(p.get_text(strip=True))
            content = ' '.join(paragraphs)
        else:
            content = 'Content not found'

        return {
            'title': title,
            'author': author,
            'publish_date': publish_date,
            'content': content,
            'source': 'TechRadar'
        }
    except Exception as e:
        print(f"Error scraping TechRadar article: {str(e)}")
        return {'title': 'Error', 'content': f'Error: {str(e)}'}

def scrape_mashable_article(url):
    try:
        response = make_request(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find title - updated class selector
        title = soup.find('h1', class_='header-100')
        title = title.get_text(strip=True) if title else 'No title found'

        # Find author
        author_link = soup.find('a', href=lambda x: x and '/author/' in x)
        author = author_link.get_text(strip=True) if author_link else 'No author found'

        # Find publish date
        date_tag = soup.find('time')
        publish_date = date_tag['datetime'] if date_tag else 'No date found'

        # Find article content - look for article element with font-serif class
        article = soup.find('article', class_='font-serif')
        if article:
            # Get all paragraphs but filter out ads and unwanted content
            paragraphs = []
            for p in article.find_all('p'):
                # Skip if it's inside an ad unit or other unwanted sections
                if not p.find_parent('ins') and not p.find_parent(class_='ad-unit'):
                    paragraphs.append(p.get_text(strip=True))
            content = ' '.join(paragraphs)
        else:
            content = 'Content not found'

        return {
            'title': title,
            'author': author,
            'publish_date': publish_date,
            'content': content,
            'source': 'Mashable'
        }
    except Exception as e:
        print(f"Error scraping Mashable article: {str(e)}")
        return {'title': 'Error', 'content': f'Error: {str(e)}'}

def scrape_gizmodo_article(url):
    try:
        response = make_request(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find title - updated selector
        title = soup.find('h1', class_='entry-title')
        title = title.get_text(strip=True) if title else 'No title found'

        # Find subtitle/excerpt
        excerpt = soup.find('div', class_='post-excerpt')
        excerpt = excerpt.get_text(strip=True) if excerpt else 'No excerpt found'

        # Find author - updated selector
        author_link = soup.find('a', href=lambda x: x and '/author/' in x)
        author = author_link.get_text(strip=True) if author_link else 'No author found'

        # Find publish date - updated selector
        date_tag = soup.find('time', class_='updated')
        publish_date = date_tag['datetime'] if date_tag else 'No date found'

        # Find article content - updated selector for the new prose class
        content_div = soup.find('div', class_='prose')
        if content_div:
            # Get all paragraphs but filter out ads and unwanted content
            paragraphs = []
            for p in content_div.find_all('p'):
                # Skip if it's inside an ad unit or other unwanted sections
                if not p.find_parent('div', class_='not-prose'):
                    paragraphs.append(p.get_text(strip=True))
            content = ' '.join(paragraphs)
        else:
            content = 'Content not found'

        return {
            'title': title,
            'excerpt': excerpt,
            'author': author,
            'publish_date': publish_date,
            'content': content,
            'source': 'Gizmodo'
        }
    except Exception as e:
        print(f"Error scraping Gizmodo article: {str(e)}")
        return {'title': 'Error', 'content': f'Error: {str(e)}'}

if __name__ == "__main__":
    # Test the scrapers
    print("Testing TechCrunch scraper...")
    techcrunch_articles = scrape_techcrunch_rss()
    if techcrunch_articles:
        print(f"Found {len(techcrunch_articles)} TechCrunch articles")
        print(f"First article title: {techcrunch_articles[0]['title']}")
    
    print("\nTesting Medium scraper...")
    medium_articles = scrape_medium_topics(num_articles_per_topic=2)
    if medium_articles:
        print(f"Found {len(medium_articles)} Medium articles")
        if medium_articles:
            print(f"First article title: {medium_articles[0]['title']}")