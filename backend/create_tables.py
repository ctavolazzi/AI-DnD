"""Script to create database tables from SQLAlchemy models"""
from app.database import Base, engine
from app.models import GameSession, Character, Location, Event

# Create all tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✓ Database tables created successfully!")
print("Tables created:")
for table_name in Base.metadata.tables.keys():
    print(f"  - {table_name}")
