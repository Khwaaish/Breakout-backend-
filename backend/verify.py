"""
Verification script to test the FastAPI setup
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app import models
import json

print("=" * 60)
print("CLOSIRA BACKEND - VERIFICATION REPORT")
print("=" * 60)

# 1. Check database configuration
print("\n✓ Database Configuration:")
print(f"  - Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./closira.db')}")

# 2. Create tables
print("\n✓ Creating Database Tables:")
try:
    Base.metadata.create_all(bind=engine)
    print("  - Tables created successfully")
except Exception as e:
    print(f"  - ERROR: {e}")

# 3. Verify tables were created
print("\n✓ Database Tables:")
inspector = __import__('sqlalchemy').inspect(engine)
tables = inspector.get_table_names()
for table in tables:
    print(f"  - {table}")

# 4. Check models
print("\n✓ Available Models:")
models_list = [attr for attr in dir(models) if not attr.startswith('_')]
for model in models_list:
    if model not in ['Base', 'Column', 'Integer', 'String', 'DateTime', 'Float', 'Boolean', 'datetime']:
        print(f"  - {model}")

# 5. Check FastAPI setup
print("\n✓ FastAPI Application:")
try:
    from main import app
    print(f"  - Title: {app.title}")
    print(f"  - Version: {app.version}")
    print(f"  - Routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"    - {', '.join(route.methods)} {route.path}")
except Exception as e:
    print(f"  - ERROR: {e}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
