from email_template import generate_email_content
import os

def preview_email_template(sample_data=None):
    """
    Generate a preview of the email template and open it in the default browser
    """
    # Create sample data if none is provided
    if sample_data is None:
        sample_data = {
            "AI": [
                (
                    {"title": "ChatGPT's Mac app gets a glowup", "link": "https://example.com/article1"},
                    "OpenAI releases Mac desktop ChatGPT features with improved coding capabilities."
                ),
                (
                    {"title": "New ML Framework Released", "link": "https://example.com/article2"},
                    "Google announces TensorFlow 3.0 with enhanced performance and new APIs."
                )
            ],
            "Web Development": [
                (
                    {"title": "React 19 Released", "link": "https://example.com/article3"},
                    "React 19 brings server components and improved performance to frontend development."
                )
            ],
            "Cybersecurity": [
                (
                    {"title": "Major Security Vulnerability Found", "link": "https://example.com/article4"},
                    "Researchers discover critical vulnerability affecting millions of devices worldwide."
                )
            ]
        }
    
    # Generate email content
    email_content = generate_email_content(sample_data)
    
    # Save to an HTML file
    preview_path = os.path.join(os.path.dirname(__file__), "email_preview.html")
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(email_content)
    
    # Open in default browser
    import webbrowser
    webbrowser.open('file://' + os.path.realpath(preview_path))
    
    print(f"Email preview saved to: {preview_path}")
    return preview_path

if __name__ == "__main__":
    # Create a preview with sample data
    preview_email_template()