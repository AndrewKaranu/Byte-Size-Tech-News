import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

app = Flask(__name__)

# Use the centralized config system
from config import Config
app.config.from_object(Config)

from flask_cors import CORS

# ... other imports and configurations ...

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization", "Admin-Key"])
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes
