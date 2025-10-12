"""
Database initialization script
"""
from app.database import init_db, engine
from app.models import (
    Horoscope,
    SajuInterpretation,
    UserRequest,
    UserFeedback,
    ModelVersion
)

def main():
    """Initialize database tables"""
    print("Creating database tables...")
    init_db()
    print("✅ Database tables created successfully!")
    
    # Print table names
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated tables: {', '.join(tables)}")

if __name__ == "__main__":
    main()
