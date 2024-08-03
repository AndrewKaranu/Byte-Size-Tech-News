import os
import json

# Load configuration from the config.json file
basedir = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(basedir, 'config.json')

with open(config_path, 'r') as config_file:
    config_data = json.load(config_file)

class Config:
    SECRET_KEY = config_data.get('SECRET_KEY', 'you-will-never-guess')
    SQLALCHEMY_DATABASE_URI = config_data.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
