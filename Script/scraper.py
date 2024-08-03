import requests
from bs4 import BeautifulSoup
import feedparser
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup
import feedparser

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
            'publication_date': publication_date
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
            'pubDate': entry.published or 'No publication date found',
            'thumbnail_url': entry.get('media_thumbnail', [{}])[0].get('url', 'No thumbnail') if entry.get('media_thumbnail') else 'No thumbnail',
            'content_url': entry.get('media_content', [{}])[0].get('url', 'No content') if entry.get('media_content') else 'No content',
            'creator': entry.get('dc_creator', 'Unknown'),
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
            'author': entry.get('author', 'Unknown')
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
            'author': entry.get('author', 'Unknown')
        })
    
    return articles


def get_techcrunch_article(url):
    response = requests.get(url)
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
        'content': content
    }



def scrape_verge_article(url):
    response = requests.get(url)
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
        'image_url': image_url
    }

# Scraping articles from Cnet.com


def scrape_cnet_article(url):
    response = requests.get(url)
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

    figure_tag = soup.find('figure', class_='c-shortcodeImage-hero')
    image_url = figure_tag.find('img')['src'] if figure_tag and figure_tag.find('img') else 'No image found'

    return {
        'title': title,
        'author': author,
        'publish_date': publish_date,
        'content': content,
        'image_url': image_url
    }


def scrape_eurogamer_article(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h1', class_='title')
    title = title.get_text(strip=True) if title else 'No title found'

    strapline = soup.find('p', class_='strapline')
    strapline = strapline.get_text(strip=True) if strapline else 'No strapline found'

    image_url_tag = soup.find('figure', class_='headline_image_wrapper').find('img') if soup.find('figure', class_='headline_image_wrapper') else None
    image_url = image_url_tag['src'] if image_url_tag else 'No image found'

    author = soup.find('span', class_='author')
    author = author.get_text(strip=True) if author else 'No author found'

    publication_date = soup.find('time')
    publication_date = publication_date['datetime'] if publication_date else 'No date found'

    comments_link = soup.find('a', class_='comments__link')
    comments_link = comments_link['href'] if comments_link else 'No comments link found'

    article_body = soup.find('div', class_='article_body_content')
    article_body = article_body.get_text(strip=True) if article_body else 'Content not found'

    return {
        'title': title,
        'strapline': strapline,
        'image_url': image_url,
        'author': author,
        'publication_date': publication_date,
        'comments_link': comments_link,
        'article_body': article_body
    }



def scrape_techradar_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h1')
    title = title.get_text(strip=True) if title else 'No title found'

    author_tag = soup.find('a', class_='author')
    author = author_tag.get_text(strip=True) if author_tag else 'No author found'

    publish_date_tag = soup.find('time')
    publish_date = publish_date_tag['datetime'] if publish_date_tag else 'No date found'

    content_div = soup.find('div', class_='article-body')
    content = ' '.join(p.get_text(strip=True) for p in content_div.find_all('p')) if content_div else 'Content not found'

    image_tag = soup.find('figure', class_='article-image').find('img') if soup.find('figure', class_='article-image') else None
    image_url = image_tag['src'] if image_tag else 'No image found'

    return {
        'title': title,
        'author': author,
        'publish_date': publish_date,
        'content': content,
        'image_url': image_url
    }



def scrape_mashable_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h1', class_='article-title')
    title = title.get_text(strip=True) if title else 'No title found'

    author = soup.find('a', class_='author')
    author = author.get_text(strip=True) if author else 'No author found'

    date_tag = soup.find('time', class_='article-date')
    publish_date = date_tag['datetime'] if date_tag else 'No date found'

    content_div = soup.find('div', class_='article-body')
    content = ' '.join(p.get_text(strip=True) for p in content_div.find_all('p')) if content_div else 'Content not found'

    image_tag = soup.find('figure', class_='article-image').find('img') if soup.find('figure', class_='article-image') else None
    image_url = image_tag['src'] if image_tag else 'No image found'

    return {
        'title': title,
        'author': author,
        'publish_date': publish_date,
        'content': content,
        'image_url': image_url
    }



def scrape_gizmodo_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h1', class_='headline')
    title = title.get_text(strip=True) if title else 'No title found'

    author = soup.find('a', class_='author')
    author = author.get_text(strip=True) if author else 'No author found'

    date_tag = soup.find('time', class_='timestamp')
    publish_date = date_tag['datetime'] if date_tag else 'No date found'

    content_div = soup.find('div', class_='article-body')
    content = ' '.join(p.get_text(strip=True) for p in content_div.find_all('p')) if content_div else 'Content not found'

    image_tag = soup.find('figure', class_='image').find('img') if soup.find('figure', class_='image') else None
    image_url = image_tag['src'] if image_tag else 'No image found'

    return {
        'title': title,
        'author': author,
        'publish_date': publish_date,
        'content': content,
        'image_url': image_url
    }

if __name__ == "__main__":
    
    # print(scrape_cnet_article("https://www.cnet.com/tech/computing/calling-bs-on-ai-hallucinations-youtube-transcripts-co-opted-by-big-tech-as-training-fodder/"))
    print(get_techcrunch_article("https://techcrunch.com/2024/07/24/tiktok-lite-exposes-users-to-harmful-content-say-mozilla-researchers/"))