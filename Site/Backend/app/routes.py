from flask import Flask, request, jsonify, current_app
from app import app, db
from app.models import User, ArticleBatch, AdminSettings
from app.services.newsletter_service import (
    collect_and_process_articles, select_articles_automatically,
    get_latest_batch, generate_preview_content, add_custom_article,
    finalize_newsletter, get_selected_articles
)
from app.services.email_service import send_newsletter, send_newsletter_preview, test_email_connection
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
import json
import re

def safe_json_loads(json_string):
    """Safely parse JSON with error handling for MySQL Unicode issues"""
    if not json_string:
        return {}
    
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Problematic JSON (first 200 chars): {json_string[:200]}")
        
        # Try to fix common Unicode escape issues
        try:
            # Remove incomplete Unicode escapes
            fixed_string = re.sub(r'\\u[0-9a-fA-F]{0,3}(?![0-9a-fA-F])', '', json_string)
            return json.loads(fixed_string)
        except json.JSONDecodeError:
            try:
                # Try removing all potentially problematic Unicode sequences
                fixed_string = re.sub(r'\\u[^"]*(?![0-9a-fA-F]{4})', '', json_string)
                return json.loads(fixed_string)
            except json.JSONDecodeError:
                print(f"Could not fix JSON string. Returning empty dict.")
                return {}

def safe_json_dumps(data):
    """Safely serialize data to JSON"""
    try:
        return json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        print(f"JSON serialization error: {e}")
        # Fallback with ASCII encoding
        return json.dumps(data, ensure_ascii=True)
import json
import os

# Admin Authentication Middleware
def get_admin_key():
    """Helper function to get admin key from Flask config"""
    return current_app.config.get('ADMIN_KEY')

# Admin Authentication Middleware
def requires_admin(f):
    def decorated(*args, **kwargs):
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = {}
        admin_key = data.get('admin_key') or request.headers.get('Admin-Key')
        expected_key = get_admin_key()

        if not admin_key or admin_key != expected_key:
            return jsonify({'error': 'Unauthorized'}), 401

        return f(*args, **kwargs)

    decorated.__name__ = f.__name__
    return decorated

# User signup endpoint (existing)
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    language = data.get('language')

    if not email or not language:
        return jsonify({'error': 'Email and language are required'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 409

    new_user = User(email=email, language=language)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User signed up successfully'}), 200

# Admin endpoints
@app.route('/admin/collect-articles', methods=['POST'])
@requires_admin
def admin_collect_articles():
    try:
        batch_id = collect_and_process_articles()
        return jsonify({
            'message': 'Articles collected successfully',
            'batch_id': batch_id
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/batches', methods=['GET'])
@requires_admin
def admin_get_batches():
    try:
        batches = ArticleBatch.query.order_by(ArticleBatch.date_created.desc()).all()
        return jsonify({
            'batches': [{
                'id': batch.id,
                'date_created': batch.date_created.isoformat(),
                'is_finalized': batch.is_finalized,
                'is_sent': batch.is_sent,
                'admin_approved': batch.admin_approved
            } for batch in batches]
        }), 200
    except Exception as e:
        print(f"Error in admin_get_batches: {str(e)}")  # Added logging
        return jsonify({'error': str(e)}), 500
    


@app.route('/admin/articles/<int:batch_id>', methods=['GET'])
@requires_admin
def admin_get_articles(batch_id):
    try:
        batch = ArticleBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
            
        articles_data = safe_json_loads(batch.articles_json)
        return jsonify({
            'batch_id': batch.id,
            'date_created': batch.date_created.isoformat(),
            'specific_articles': articles_data.get('specific_articles', {}),
            'general_articles': articles_data.get('general_articles', [])
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/auto-select/<int:batch_id>', methods=['POST'])
@requires_admin
def admin_auto_select(batch_id):
    try:
        selected = select_articles_automatically(batch_id)
        return jsonify({
            'message': 'Articles auto-selected successfully',
            'selected_articles': selected
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/admin/select-article/<int:batch_id>', methods=['POST'])
@requires_admin
def admin_select_article(batch_id):
    try:
        data = request.get_json()
        article_id = data.get('article_id')
        topic = data.get('topic')

        batch = ArticleBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        articles_data = safe_json_loads(batch.articles_json)

        # Find the article in the specific or general articles
        article_to_add = None

        # Search in specific articles
        if topic in articles_data.get('specific_articles', {}):
            article_to_add = next(
                (article for article in articles_data['specific_articles'][topic] if article.get('id') == article_id),
                None
            )

        # Search in general articles if not found in specific articles
        if not article_to_add:
            article_to_add = next(
                (article for article in articles_data.get('general_articles', []) if article.get('id') == article_id),
                None
            )

        if not article_to_add:
            return jsonify({'error': 'Article not found in batch'}), 404

        # Add or remove from selected articles
        selected = safe_json_loads(batch.selected_json) if batch.selected_json else {}

        if topic not in selected:
            selected[topic] = []

        # Check if the article is already selected
        is_selected = any(article.get('id') == article_id for article in selected[topic])

        if is_selected:
            # Remove the article
            selected[topic] = [article for article in selected[topic] if article.get('id') != article_id]
            if not selected[topic]:
                del selected[topic]  # Remove the topic if it's empty
            message = 'Article deselected successfully'
        else:
            # Add the article
            selected[topic].append(article_to_add)
            message = 'Article selected successfully'

        batch.selected_json = safe_json_dumps(selected)
        db.session.commit()

        return jsonify({
            'message': message,
            'article': article_to_add
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/selected-articles/<int:batch_id>', methods=['GET'])
@requires_admin
def admin_get_selected_articles(batch_id):
    try:
        batch = ArticleBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        selected_articles = safe_json_loads(batch.selected_json) if batch.selected_json else {}
        
        # Debug info
        print(f"Selected articles for batch {batch_id}:")
        print(json.dumps(selected_articles, indent=2))
        
        return jsonify({'selected_articles': selected_articles}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/admin/reset-selection/<int:batch_id>', methods=['POST'])
@requires_admin
def admin_reset_selection(batch_id):
    try:
        batch = ArticleBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
        
        # Reset selected articles
        batch.selected_json = '{}'
        batch.selected_articles = 0
        db.session.commit()
        
        return jsonify({'message': 'Selection reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/add-custom-article/<int:batch_id>', methods=['POST'])
@requires_admin
def admin_add_custom_article(batch_id):
    try:
        data = request.get_json()
        title = data.get('title')
        link = data.get('link')
        summary = data.get('summary')
        topic = data.get('topic')
        
        if not all([title, link, summary, topic]):
            return jsonify({'error': 'All fields are required'}), 400
        
        article = add_custom_article(batch_id, title, link, summary, topic)
        
        return jsonify({
            'message': 'Custom article added successfully',
            'article': article
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/preview/<int:batch_id>', methods=['GET'])
@requires_admin
def admin_preview(batch_id):
    try:
        email_content = generate_preview_content(batch_id)
        return jsonify({
            'email_content': email_content
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/send-preview/<int:batch_id>', methods=['POST'])
@requires_admin
def admin_send_preview(batch_id):
    try:
        data = request.get_json()
        admin_email = data.get('admin_email')
        
        if not admin_email:
            return jsonify({'error': 'Admin email is required'}), 400
        
        email_content = generate_preview_content(batch_id)
        result = send_newsletter_preview(email_content, admin_email)
        
        if result:
            return jsonify({'message': 'Preview sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send preview'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/approve/<int:batch_id>', methods=['POST'])
@requires_admin
def admin_approve(batch_id):
    try:
        batch = ArticleBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
        
        # Finalize the newsletter content if not already finalized
        if not batch.email_content:
            finalize_newsletter(batch_id)
        
        batch.admin_approved = True
        db.session.commit()
        
        return jsonify({'message': 'Newsletter approved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/send-newsletter/<int:batch_id>', methods=['POST'])
@requires_admin
def admin_send_newsletter(batch_id):
    try:
        batch = ArticleBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
        
        if not batch.admin_approved:
            return jsonify({'error': 'Newsletter not yet approved'}), 400
        
        result = send_newsletter(batch_id)
        
        return jsonify({
            'message': 'Newsletter sent successfully',
            'stats': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/verify', methods=['GET'])
def admin_verify():
    """Simple endpoint to verify admin key reading from config"""
    admin_key = request.headers.get('Admin-Key')
    
    # Use the same approach as other endpoints
    expected_key = get_admin_key()
    
    print(f"Received key: '{admin_key}'")
    print(f"Expected key from config: '{expected_key}'")
    print(f"Keys match: {admin_key == expected_key}")
    
    if admin_key and admin_key == expected_key:
        return jsonify({'authenticated': True}), 200
    else:
        return jsonify({'authenticated': False, 'error': 'Invalid admin key'}), 401

@app.route('/admin/test-email', methods=['POST'])
@requires_admin
def admin_test_email():
    """Test email configuration"""
    try:
        result = test_email_connection()
        if result:
            return jsonify({'success': True, 'message': 'Email connection test successful'}), 200
        else:
            return jsonify({'success': False, 'message': 'Email connection test failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/test-database', methods=['POST'])
@requires_admin
def admin_test_database():
    """Test database connection"""
    try:
        # Test database connection
        db.engine.execute('SELECT 1')
        
        # Get database info
        db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        db_type = 'MySQL' if 'mysql' in db_url else 'SQLite' if 'sqlite' in db_url else 'Unknown'
        
        return jsonify({
            'success': True, 
            'message': f'Database connection test successful',
            'database_type': db_type,
            'database_url': db_url.split('@')[-1] if '@' in db_url else db_url  # Hide credentials
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/settings', methods=['GET', 'POST'])
@requires_admin
def admin_settings():
    try:
        settings = AdminSettings.query.first()
        if not settings:
            settings = AdminSettings()
            db.session.add(settings)
            db.session.commit()
        
        if request.method == 'POST':
            data = request.get_json()
            
            if 'collection_time' in data:
                hour, minute = map(int, data['collection_time'].split(':'))
                settings.collection_time = time(hour, minute)
            
            if 'admin_review_time' in data:
                hour, minute = map(int, data['admin_review_time'].split(':'))
                settings.admin_review_time = time(hour, minute)
            
            if 'send_time' in data:
                hour, minute = map(int, data['send_time'].split(':'))
                settings.send_time = time(hour, minute)
            
            if 'admin_email' in data:
                settings.admin_email = data['admin_email']
            
            if 'auto_approve' in data:
                settings.auto_approve = data['auto_approve']
            
            db.session.commit()
            
            # Update scheduler
            update_scheduler()
            
            return jsonify({'message': 'Settings updated successfully'}), 200
        else:
            return jsonify({
                'collection_time': f"{settings.collection_time.hour:02d}:{settings.collection_time.minute:02d}",
                'admin_review_time': f"{settings.admin_review_time.hour:02d}:{settings.admin_review_time.minute:02d}",
                'send_time': f"{settings.send_time.hour:02d}:{settings.send_time.minute:02d}",
                'admin_email': settings.admin_email,
                'auto_approve': settings.auto_approve
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/users', methods=['GET'])
@requires_admin
def admin_get_users():
    """Get list of all registered users"""
    users = User.query.all()
    user_list = []
    for u in users:
        user_list.append({
            'id': u.id,
            'email': u.email,
            'language': u.language,
            'is_admin': u.is_admin
        })
    return jsonify({'users': user_list}), 200

@app.route('/admin/users/<int:user_id>', methods=['PUT'])
@requires_admin
def admin_update_user(user_id):
    """Update user information"""
    data = request.get_json() or {}
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if 'email' in data:
        user.email = data['email']
    if 'language' in data:
        user.language = data['language']
    if 'is_admin' in data:
        user.is_admin = data['is_admin']
    db.session.commit()
    return jsonify({
        'message': 'User updated successfully',
        'user': {
            'id': user.id,
            'email': user.email,
            'language': user.language,
            'is_admin': user.is_admin
        }
    }), 200

# Scheduler functions
scheduler = BackgroundScheduler()

def scheduled_article_collection():
    """Collect and process articles automatically"""
    with app.app_context():
        try:
            print(f"[{datetime.now()}] Scheduled article collection started")
            batch_id = collect_and_process_articles()
            print(f"[{datetime.now()}] Scheduled article collection completed, batch_id: {batch_id}")
        except Exception as e:
            print(f"[{datetime.now()}] Error in scheduled article collection: {str(e)}")

def scheduled_admin_reminder():
    """Send reminder to admin if no selection has been made"""
    with app.app_context():
        try:
            settings = AdminSettings.query.first()
            if not settings or not settings.admin_email:
                print("No admin email configured for reminders")
                return
            
            latest_batch = get_latest_batch()
            if not latest_batch or latest_batch.is_finalized or latest_batch.selected_json:
                # No action needed if already finalized or selections made
                return
                
            # Send reminder email to admin
            ses = boto3.client(
                'ses',
                region_name=current_app.config.get('AWS_REGION'),
                aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY'),
                aws_secret_access_key=current_app.config.get('AWS_SECRET_KEY')
            )
            
            admin_url = f"{current_app.config.get('ADMIN_URL', 'http://localhost:3000/admin')}"
            
            ses.send_email(
                Source=current_app.config.get('EMAIL_SENDER'),
                Destination={
                    'ToAddresses': [settings.admin_email]
                },
                Message={
                    'Subject': {
                        'Data': 'Action Required: Newsletter Article Selection',
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': f"""
                            <p>Hello Admin,</p>
                            <p>This is a reminder that you have not yet selected articles for today's newsletter.</p>
                            <p>If no selection is made, articles will be automatically selected and sent at {settings.send_time.hour:02d}:{settings.send_time.minute:02d}.</p>
                            <p><a href="{admin_url}">Click here to access the admin panel</a></p>
                            """,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            print(f"[{datetime.now()}] Admin reminder email sent to {settings.admin_email}")
        except Exception as e:
            print(f"[{datetime.now()}] Error sending admin reminder: {str(e)}")

def scheduled_newsletter_dispatch():
    """Finalize and send the newsletter if approved or auto-approve is enabled"""
    with app.app_context():
        try:
            settings = AdminSettings.query.first()
            latest_batch = get_latest_batch()
            
            if not latest_batch:
                print("No article batch found for scheduled dispatch")
                return
            
            if latest_batch.is_sent:
                print("Latest batch already sent")
                return
                
            # If auto-approve is enabled or the batch is already approved
            if settings and settings.auto_approve or latest_batch.admin_approved:
                # Finalize the newsletter if not already done
                if not latest_batch.email_content:
                    finalize_newsletter(latest_batch.id)
                
                # Send the newsletter
                result = send_newsletter(latest_batch.id)
                print(f"[{datetime.now()}] Newsletter automatically sent. Stats: {result}")
            else:
                print(f"[{datetime.now()}] Newsletter not sent - waiting for admin approval")
        except Exception as e:
            print(f"[{datetime.now()}] Error in scheduled newsletter dispatch: {str(e)}")

def update_scheduler():
    """Update scheduler jobs based on admin settings"""
    settings = AdminSettings.query.first()
    if not settings:
        print("No settings found, using default schedule")
        return
    
    # Remove existing jobs
    scheduler.remove_all_jobs()
    
    # Add article collection job
    scheduler.add_job(
        scheduled_article_collection, 
        CronTrigger(
            hour=settings.collection_time.hour,
            minute=settings.collection_time.minute
        ),
        id='article_collection'
    )
    
    # Add admin reminder job
    scheduler.add_job(
        scheduled_admin_reminder, 
        CronTrigger(
            hour=settings.admin_review_time.hour,
            minute=settings.admin_review_time.minute
        ),
        id='admin_reminder'
    )
    
    # Add newsletter dispatch job
    scheduler.add_job(
        scheduled_newsletter_dispatch, 
        CronTrigger(
            hour=settings.send_time.hour,
            minute=settings.send_time.minute
        ),
        id='newsletter_dispatch'
    )
    
    print(f"Scheduler updated with: collection at {settings.collection_time.hour:02d}:{settings.collection_time.minute:02d}, "
          f"reminder at {settings.admin_review_time.hour:02d}:{settings.admin_review_time.minute:02d}, "
          f"dispatch at {settings.send_time.hour:02d}:{settings.send_time.minute:02d}")

# Initialize scheduler
with app.app_context():
    def initialize_app():
        if not scheduler.running:
            # Set up default jobs
            scheduler.add_job(
                scheduled_article_collection, 
                'cron', 
                hour=5,  # 5 AM
                id='article_collection'
            )
            scheduler.add_job(
                scheduled_admin_reminder, 
                'cron', 
                hour=14,  # 2 PM
                id='admin_reminder'
            )
            scheduler.add_job(
                scheduled_newsletter_dispatch, 
                'cron', 
                hour=16,  # 4 PM
                id='newsletter_dispatch'
            )
            
            # Start the scheduler
            scheduler.start()
            print("Scheduler started with default times")
            
            # Update with database settings if available
            update_scheduler()
            
@app.route('/admin/test/create-dummy-batch', methods=['POST'])
@requires_admin
def admin_create_dummy_batch():
    """Creates a batch with dummy data for testing"""
    try:
        # Create a dummy batch with sample articles
        batch = ArticleBatch(
            date_created=datetime.now(),
            is_finalized=False,
            is_sent=False,
            admin_approved=False
        )
        
        # Sample articles data
        dummy_articles = {
            "specific_articles": {
                "AI and Machine Learning": [
                    {
                        "id": "ai001",
                        "title": "New AI Model Breaks Performance Records",
                        "url": "https://example.com/ai-news-1",
                        "summary": "A groundbreaking new AI model has achieved state-of-the-art results across multiple benchmarks.",
                        "source": "Tech Journal"
                    },
                    {
                        "id": "ai002",
                        "title": "Machine Learning Applications in Healthcare",
                        "url": "https://example.com/ai-news-2",
                        "summary": "How ML is transforming patient diagnosis and treatment planning.",
                        "source": "Health Tech Today"
                    }
                ],
                "Cybersecurity": [
                    {
                        "id": "sec001",
                        "title": "Major Security Vulnerability Discovered",
                        "url": "https://example.com/security-news-1",
                        "summary": "Researchers have identified a critical vulnerability affecting millions of devices.",
                        "source": "Security Weekly"
                    }
                ],
                "Software Development": [
                    {
                        "id": "dev001",
                        "title": "TypeScript 5.0 Released",
                        "url": "https://example.com/dev-news-1",
                        "summary": "The latest version brings performance improvements and new language features.",
                        "source": "Dev Insider"
                    }
                ]
            },
            "general_articles": [
                {
                    "id": "gen001",
                    "title": "Tech Company Stock Soars After Earnings Report",
                    "url": "https://example.com/business-news-1",
                    "summary": "Shares increased by 15% following better-than-expected quarterly results.",
                    "source": "Business Tech",
                    "topics": ["Business", "Tech Industry"]
                },
                {
                    "id": "gen002",
                    "title": "New Gaming Console Sets Pre-order Records",
                    "url": "https://example.com/gaming-news-1",
                    "summary": "The highly anticipated next-gen gaming system has broken pre-sale records.",
                    "source": "Gaming Now",
                    "topics": ["Gaming", "Hardware"]
                }
            ]
        }
        
        batch.articles_json = json.dumps(dummy_articles)
        batch.total_articles = (
            len(dummy_articles["general_articles"]) + 
            sum(len(articles) for articles in dummy_articles["specific_articles"].values())
        )
        
        # Add some selected articles
        selected = {
            "AI and Machine Learning": [dummy_articles["specific_articles"]["AI and Machine Learning"][0]],
            "Cybersecurity": [dummy_articles["specific_articles"]["Cybersecurity"][0]],
            "General": [dummy_articles["general_articles"][0]]
        }
        batch.selected_json = json.dumps(selected)
        batch.selected_articles = sum(len(articles) for articles in selected.values())
        
        # Add to database
        db.session.add(batch)
        db.session.commit()
        
        return jsonify({
            'message': 'Dummy batch created successfully',
            'batch_id': batch.id,
            'date_created': batch.date_created.isoformat(),
            'total_articles': batch.total_articles,
            'selected_articles': batch.selected_articles
        }), 200
    except Exception as e:
        print(f"Error creating dummy batch: {str(e)}")
        return jsonify({'error': str(e)}), 500