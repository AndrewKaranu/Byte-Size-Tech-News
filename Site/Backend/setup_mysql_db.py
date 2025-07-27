#!/usr/bin/env python3
"""
MySQL Database Setup Script for AWS RDS
"""

import pymysql

def create_database():
    """Create the database if it doesn't exist"""
    
    # Connection config without specifying the database
    config = {
        'host': 'bytesizeddb.cxo0g8oai6k9.us-west-2.rds.amazonaws.com',
        'port': 3306,
        'user': 'Issandrew',
        'password': 'Lqvgfaqp4qi76DEOYSso',
        'connect_timeout': 10,
        'charset': 'utf8mb4'
    }
    
    database_name = 'bytesizeddb'
    
    print(f"🔍 Connecting to MySQL server...")
    
    try:
        # Connect without specifying database
        connection = pymysql.connect(**config)
        print("✅ Connected to MySQL server")
        
        with connection.cursor() as cursor:
            # Check if database exists
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            
            if database_name in databases:
                print(f"✅ Database '{database_name}' already exists")
            else:
                print(f"🔨 Creating database '{database_name}'...")
                cursor.execute(f"CREATE DATABASE {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✅ Database '{database_name}' created successfully")
            
            # Test connection to the specific database
            print(f"🔍 Testing connection to database '{database_name}'...")
            cursor.execute(f"USE {database_name}")
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            print(f"✅ Successfully connected to database: {current_db}")
            
        connection.close()
        return True
        
    except pymysql.err.OperationalError as e:
        error_code, error_msg = e.args
        print(f"❌ MySQL operation failed: {error_msg}")
        
        if error_code == 1045:
            print("💡 Access denied - check username and password")
        elif error_code == 2003:
            print("💡 Can't connect to server - check host, port, and network access")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database_connection():
    """Test connection to the specific database"""
    config = {
        'host': 'bytesizeddb.cxo0g8oai6k9.us-west-2.rds.amazonaws.com',
        'port': 3306,
        'user': 'Issandrew',
        'password': 'Lqvgfaqp4qi76DEOYSso',
        'database': 'bytesizeddb',
        'connect_timeout': 10,
        'charset': 'utf8mb4'
    }
    
    print(f"🔍 Testing connection to database 'bytesizeddb'...")
    
    try:
        connection = pymysql.connect(**config)
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"✅ Connected to MySQL version: {version}")
            
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            print(f"✅ Current database: {current_db}")
            
            # Show tables (should be empty for new database)
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if tables:
                print(f"📋 Existing tables: {[table[0] for table in tables]}")
            else:
                print("📋 No tables found (empty database)")
            
        connection.close()
        return True
        
    except pymysql.err.OperationalError as e:
        error_code, error_msg = e.args
        print(f"❌ Database connection failed: {error_msg}")
        return False

if __name__ == "__main__":
    print("🚀 MySQL Database Setup")
    print("=" * 50)
    
    # Step 1: Create database if needed
    if create_database():
        print("\n" + "=" * 50)
        # Step 2: Test connection to the database
        test_database_connection()
        
        print("\n" + "=" * 50)
        print("🎉 Database setup complete!")
        print("💡 You can now enable MySQL in your config:")
        print('   Set "USE_MYSQL": true in config.json')
    else:
        print("\n❌ Database setup failed!")
