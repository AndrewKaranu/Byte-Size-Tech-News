import boto3
from app import app, db
from app.models import User, ArticleBatch
from flask import current_app

def send_newsletter_preview(email_content, admin_email):
    """Send a preview newsletter to the admin email"""
    ses = boto3.client(
        'ses',
        region_name=current_app.config.get('AWS_REGION'),
        aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY'),
        aws_secret_access_key=current_app.config.get('AWS_SECRET_KEY')
    )
    
    try:
        response = ses.send_email(
            Source=current_app.config.get('EMAIL_SENDER'),
            Destination={
                'ToAddresses': [admin_email]
            },
            Message={
                'Subject': {
                    'Data': '[PREVIEW] Byte Sized Tech News - For Your Approval',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': email_content,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print(f"Preview email sent to {admin_email}, MessageId: {response['MessageId']}")
        return True
    except Exception as e:
        print(f"Error sending preview email: {str(e)}")
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
    
    # Initialize AWS SES client
    ses = boto3.client(
        'ses',
        region_name=current_app.config.get('AWS_REGION'),
        aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY'),
        aws_secret_access_key=current_app.config.get('AWS_SECRET_KEY')
    )
    
    # Get all subscribed users
    users = User.query.filter_by(is_admin=False).all()
    
    sent_count = 0
    error_count = 0
    
    # Send emails
    for user in users:
        try:
            response = ses.send_email(
                Source=current_app.config.get('EMAIL_SENDER'),
                Destination={
                    'ToAddresses': [user.email]
                },
                Message={
                    'Subject': {
                        'Data': 'Byte Sized Tech News - Latest Updates',
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': batch.email_content,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            print(f"Email sent to {user.email}, MessageId: {response['MessageId']}")
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