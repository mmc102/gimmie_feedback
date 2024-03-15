from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Event, Presentation, Base

# Database connection string
DATABASE_URL =  "postgresql://postgres:mysecretpassword@localhost:6969/postgres"

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Define event data
event_data = {
    "name": "Example Event",
    "date": "2024-03-16"  # Replace with the actual date
}

# Insert event into the database
event = Event(**event_data)
session.add(event)
session.commit()

# Optionally, define and insert presentation data for the event
presentation_data = [
    {"title": "Presentation 1", "description": "Description of Presentation 1", "event_id": event.id},
    {"title": "Presentation 2", "description": "Description of Presentation 2", "event_id": event.id},
]

for presentation_info in presentation_data:
    presentation = Presentation(**presentation_info)
    session.add(presentation)

session.commit()

print("Event seeded successfully.")
