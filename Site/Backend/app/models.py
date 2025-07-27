from app import db
from datetime import datetime,time
from sqlalchemy.dialects.mysql import LONGTEXT

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    language = db.Column(db.String(10), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.email}>'

class ArticleBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    articles_json = db.Column(LONGTEXT)  # JSON string of all collected articles
    selected_json = db.Column(LONGTEXT)  # JSON string of selected articles
    email_content = db.Column(LONGTEXT)  # Final email HTML content
    is_finalized = db.Column(db.Boolean, default=False)
    is_sent = db.Column(db.Boolean, default=False)
    admin_approved = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ArticleBatch {self.date_created}>'

class SelectedArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('article_batch.id'))
    title = db.Column(db.String(200))
    link = db.Column(db.String(500))
    summary = db.Column(db.Text)
    topic = db.Column(db.String(50))
    custom = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<SelectedArticle {self.title}>'

class AdminSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_time = db.Column(db.Time, default=time(5, 0))  # 5:00 AM default
    admin_review_time = db.Column(db.Time, default=time(14, 0))  # 2:00 PM default
    send_time = db.Column(db.Time, default=time(16, 0))  # 4:00 PM default
    admin_email = db.Column(db.String(120))
    auto_approve = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<AdminSettings {self.id}>'