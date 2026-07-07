"""
Script to reset the database - drops and recreates all tables
"""
import pymysql
from config import Config

# Parse database URL
# Format: mysql+pymysql://username:password@host/database
db_url = Config.SQLALCHEMY_DATABASE_URI
# Remove the mysql+pymysql:// prefix
db_url = db_url.replace('mysql+pymysql://', '')

# Split into parts
if '@' in db_url:
    credentials, location = db_url.split('@')
    username, password = credentials.split(':')
    host_and_db = location.split('/')
    host = host_and_db[0]
    database = host_and_db[1] if len(host_and_db) > 1 else 'national_bookstore_scm'
else:
    print("Error: Could not parse database URL")
    exit(1)

print(f"Connecting to MySQL server at {host} as {username}...")

try:
    # Connect to MySQL server (not to specific database)
    connection = pymysql.connect(
        host=host,
        user=username,
        password=password,
        charset='utf8mb4'
    )
    
    cursor = connection.cursor()
    
    # Drop database if exists
    print(f"Dropping database '{database}' if it exists...")
    cursor.execute(f"DROP DATABASE IF EXISTS {database}")
    
    # Create fresh database
    print(f"Creating database '{database}'...")
    cursor.execute(f"CREATE DATABASE {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print("\n✅ Database reset successfully!")
    print(f"✅ Database '{database}' is ready")
    print("\nNext steps:")
    print("1. Run: python seed_data.py")
    print("2. Run: python run.py")
    
except pymysql.err.OperationalError as e:
    print(f"\n❌ Error connecting to MySQL: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure MySQL is running")
    print("2. Check username and password in config.py")
    print("3. Verify MySQL is accessible at the specified host")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
