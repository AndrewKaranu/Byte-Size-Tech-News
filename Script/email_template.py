EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tech News Digest</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; }}
        .article {{ margin-bottom: 30px; }}
        .article h3 {{ margin-bottom: 10px; }}
        .article p {{ margin-bottom: 10px; }}
        .article a {{ color: #3498db; text-decoration: none; }}
        .article a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Byte Sized Tech News</h1>
        {content}
    </div>
</body>
</html>
"""

def format_article(article, summary):
    return f"""
    <div class="article">
        <h3><a href="{article['link']}">{article['title']}</a></h3>
        <p>{summary}</p>
    </div>
    """

def generate_email_content(articles_with_summaries):
    content = ""
    for topic, topic_articles in articles_with_summaries.items():
        content += f"<h2>{topic}</h2>"
        for article, summary in topic_articles:
            content += format_article(article, summary)
    return EMAIL_TEMPLATE.format(content=content)