EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tech News Digest</title>
    <style>
        body {{ 
            font-family: 'Arial', 'MS Sans Serif', sans-serif; 
            line-height: 1.4; 
            color: #000000; 
            background-color: #c0c0c0;
            margin: 0;
            padding: 0;
        }}
        .container {{ 
            max-width: 600px; 
            margin: 20px auto; 
            padding: 3px;
            background-color: #c0c0c0; 
            border: 2px solid;
            border-color: #ffffff #808080 #808080 #ffffff;
            box-shadow: inset 1px 1px 0px #dfdfdf, inset -1px -1px 0px #0a0a0a;
        }}
        .title-bar {{
            background: linear-gradient(90deg, #000080, #1084d0);
            padding: 3px 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
            font-weight: bold;
        }}
        .window-content {{
            padding: 10px;
            background-color: #c0c0c0;
        }}
        .header {{
            text-align: center;
            margin-bottom: 15px;
            padding: 10px;
        }}
        .logo {{
            max-width: 300px;
            height: auto;
        }}
        h1 {{ margin-top: 0; font-size: 16px; }}
        h2 {{ 
            background-color: #000080; 
            color: white; 
            padding: 3px 5px; 
            font-size: 14px; 
            margin-top: 15px;
            margin-bottom: 10px;
        }}
        .article {{ 
            margin-bottom: 15px;
            border: 2px solid;
            border-color: #dfdfdf #808080 #808080 #dfdfdf;
            padding: 8px;
            background-color: #c0c0c0;
        }}
        .article h3 {{ 
            margin-top: 0;
            margin-bottom: 8px;
            font-size: 13px;
        }}
        .article p {{ 
            margin-bottom: 5px;
            font-size: 12px;
        }}
        .article a {{ 
            color: #0000ff; 
            text-decoration: none; 
        }}
        .article a:hover {{ 
            text-decoration: underline; 
        }}
        .footer {{
            margin-top: 15px;
            border-top: 1px solid #808080;
            padding-top: 10px;
            font-size: 11px;
            color: #444;
            text-align: center;
        }}
        .button {{
            display: inline-block;
            margin: 5px 0;
            padding: 5px 10px;
            background-color: #c0c0c0;
            border: 2px solid;
            border-color: #dfdfdf #808080 #808080 #dfdfdf;
            text-align: center;
            text-decoration: none;
            color: black;
            font-size: 12px;
        }}
        .button:hover {{
            background-color: #d0d0d0;
        }}
        .button-container {{
            text-align: center;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title-bar">
            <div>Byte Sized Tech News</div>
            <div>□ × </div>
        </div>
        <div class="window-content">
            <div class="header">
                <img src="{logo_url}" alt="Byte Sized Tech News" class="logo">
            </div>
            
            <div class="button-container">
                <a href="{signup_link}" class="button">Subscribe to Newsletter</a>
            </div>
            
            {content}
            
            <div class="footer">
                <p>© {current_year} Byte Sized Tech News. All rights reserved.</p>
                <div>
                    <a href="{signup_link}" class="button">Subscribe</a>
                    <a href="{unsubscribe_link}" class="button">Unsubscribe</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

import datetime

def format_article(article, summary):
    return f"""
    <div class="article">
        <h3><a href="{article['link']}">{article['title']}</a></h3>
        <p>{summary}</p>
    </div>
    """

def generate_email_content(
    articles_with_summaries, 
    logo_url="C:\\Users\\user\\Desktop\\Byte Sized Tech News\\Site\\Backend\\app\\static\\Images\\logobyte.png",
    signup_link="https://yoursite.com/signup",
    unsubscribe_link="https://yoursite.com/unsubscribe"
):
    content = ""
    for topic, topic_articles in articles_with_summaries.items():
        content += f"<h2>{topic}</h2>"
        for article, summary in topic_articles:
            content += format_article(article, summary)
    
    current_year = datetime.datetime.now().year
    return EMAIL_TEMPLATE.format(
        content=content,
        current_year=current_year,
        logo_url=logo_url,
        signup_link=signup_link,
        unsubscribe_link=unsubscribe_link
    )