from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        result = conn.execute(text('DESCRIBE article_batch'))
        print("Table schema:")
        for row in result:
            print(row)
