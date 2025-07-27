import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app import app, db
from app.models import User, ArticleBatch
from flask import current_app

def send_newsletter_preview(email_content, admin_email):
    """Send a preview newsletter to the admin email"""
    try:
        email_sender = current_app.config.get('EMAIL_SENDER')
        email_password = current_app.config.get('EMAIL_PASSWORD')
        
        print(f"Attempting to send email from: {email_sender}")
        print(f"Password configured: {'Yes' if email_password else 'No'}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '[PREVIEW] Byte Sized Tech News - For Your Approval'
        msg['From'] = email_sender
        msg['To'] = admin_email
        
        # Add HTML content
        html_part = MIMEText(email_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            print("Connecting to Gmail SMTP...")
            server.starttls()
            print("Starting TLS...")
            server.login(email_sender, email_password)
            print("Login successful!")
            server.send_message(msg)
            print("Message sent!")
        
        print(f"Preview email sent to {admin_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {str(e)}")
        print("This usually means:")
        print("1. You need to use an App Password (not your regular Gmail password)")
        print("2. 2-Factor Authentication must be enabled on your Google account")
        print("3. Check if the email address is correct")
        return False
    except Exception as e:
        print(f"Error sending preview email: {str(e)}")
        return False

def test_email_connection():
    """Test email connection and credentials"""
    try:
        email_sender = current_app.config.get('EMAIL_SENDER')
        email_password = current_app.config.get('EMAIL_PASSWORD')
        
        print(f"Testing email connection for: {email_sender}")
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_sender, email_password)
            print("✅ Email connection test successful!")
            return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("Please check:")
        print("1. Use App Password (not regular Gmail password)")
        print("2. Enable 2-Factor Authentication")
        print("3. Generate App Password from Google Account Security settings")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False

def send_newsletter(batch_id=None):
    """Send newsletter to all subscribed users"""
    # Get the latest batch if no batch_id provided
    batch = ArticleBatch.query.get(batch_id) if batch_id else ArticleBatch.query.filter_by(
        is_finalized=True, 
        is_sent=False
    ).order_by(ArticleBatch.date_created.desc()).first()
    
    if not batch or not batch.email_content:
        raise Exception("No finalized newsletter content available")
    
    # Get all subscribed users
    users = User.query.filter_by(is_admin=False).all()
    
    sent_count = 0
    error_count = 0
    
    # Send emails
    for user in users:
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Byte Sized Tech News - Latest Updates'
            msg['From'] = current_app.config.get('EMAIL_SENDER')
            msg['To'] = user.email
            
            # Add HTML content
            html_part = MIMEText(batch.email_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(
                    current_app.config.get('EMAIL_SENDER'), 
                    current_app.config.get('EMAIL_PASSWORD')
                )
                server.send_message(msg)
            
            print(f"Email sent to {user.email}")
            sent_count += 1
        except Exception as e:
            print(f"Error sending email to {user.email}: {str(e)}")
            error_count += 1
    
    # Mark the batch as sent
    batch.is_sent = True
    db.session.commit()
    
    return {
        "sent": sent_count,
        "errors": error_count,
        "total": sent_count + error_count
    }