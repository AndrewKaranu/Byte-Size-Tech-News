#!/usr/bin/env python3
"""
Database initialization script for Byte Sized Tech News
"""

import os
import sys
from flask import Flask
from flask_migrate import init, migrate, upgrade
from app import app, db

def init_database():
    """Initialize the database with migrations"""
    with app.app_context():
        try:
            print("Initializing database...")
            
            # Check if migrations folder exists
            migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
            if not os.path.exists(migrations_dir):
                print("Creating migrations repository...")
                init()
            
            # Create migration
            print("Creating migration...")
            migrate(message="Initial migration")
            
            # Apply migration
            print("Applying migration...")
            upgrade()
            
            print("✅ Database initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
            return False

def test_connection():
    """Test database connection"""
    with app.app_context():
        try:
            # Test connection using SQLAlchemy 2.x syntax
            from sqlalchemy import text
            
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"🔍 Testing connection to: {db_url.split('@')[1] if '@' in db_url else db_url}")
            
            with db.engine.connect() as connection:
                if 'mysql' in db_url:
                    db_type = "MySQL"
                    # Test MySQL specific query
                    result = connection.execute(text('SELECT VERSION()'))
                    version = result.fetchone()[0]
                    print(f"✅ Connected to {db_type} version: {version}")
                elif 'sqlite' in db_url:
                    db_type = "SQLite"
                    result = connection.execute(text('SELECT sqlite_version()'))
                    version = result.fetchone()[0]
                    print(f"✅ Connected to {db_type} version: {version}")
                else:
                    # Generic test
                    result = connection.execute(text('SELECT 1'))
                    print("✅ Database connection successful")
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            # Additional debugging info
            if 'getaddrinfo failed' in str(e):
                print("💡 This usually means the hostname cannot be resolved.")
                print("   Check that your RDS endpoint is correct and accessible.")
            elif 'Access denied' in str(e):
                print("💡 This usually means incorrect username/password.")
            elif 'Unknown database' in str(e):
                print("💡 This usually means the database name doesn't exist.")
            return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "test":
            test_connection()
        elif command == "init":
            init_database()
        else:
            print("Usage: python init_db.py [test|init]")
    else:
        print("Testing database connection...")
        if test_connection():
            print("\nInitializing database...")
            init_database()
