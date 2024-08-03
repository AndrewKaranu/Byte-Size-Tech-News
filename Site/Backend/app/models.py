from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    language = db.Column(db.String(10), nullable=False)
    
    def __repr__(self):
        return f'<User {self.email}>'
