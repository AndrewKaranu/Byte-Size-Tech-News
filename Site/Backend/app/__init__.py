import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

app = Flask(__name__)

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

app.config['SECRET_KEY'] = config.get('SECRET_KEY', 'you-will-never-guess')
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from flask_cors import CORS

# ... other imports and configurations ...

CORS(app, resources={r"/*": {"origins": "*"}})
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes
