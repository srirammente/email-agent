from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import TypeDecorator, TEXT # Import TypeDecorator and TEXT
from datetime import datetime
import os
import json
from typing import List, Dict, Any

# Custom type for JSON data in SQLite
class SQLiteJSON(TypeDecorator):
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


# Database connection URL from environment variable (for SQLite)
# SQLite database file will be created in the backend directory
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./email_agent.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # Needed for SQLite with FastAPI
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True, index=True)
    sender = Column(String, index=True)
    subject = Column(String)
    body = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)
    category = Column(String, nullable=True)
    action_items = Column(SQLiteJSON, nullable=True) # Use custom JSON type
    summary = Column(Text, nullable=True)
    processed = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Email(id='{self.id}', subject='{self.subject}')>"

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g., 'categorization', 'action_item'
    template = Column(Text)

    def __repr__(self):
        return f"<Prompt(name='{self.name}')>"

class Draft(Base):
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String) # Link to the email it's a reply to
    subject = Column(String)
    body = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # New fields for output requirements
    suggested_follow_ups = Column(SQLiteJSON, nullable=True) # Use custom JSON type
    draft_metadata = Column(SQLiteJSON, nullable=True) # Use custom JSON type (renamed from 'metadata' to avoid SQLAlchemy conflict)

    def __repr__(self):
        return f"<Draft(id={self.id}, subject='{self.subject}')>"

def create_db_tables():
    """Creates all defined database tables if they do not already exist."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if they didn't exist).")

def seed_initial_prompts():
    from sqlalchemy.orm import Session
    db = SessionLocal()
    try:
        default_prompts = [
            {"name": "categorization", "template": """Categorize emails into: Important, Newsletter, Spam, To-Do.
To-Do emails must include a direct request requiring user action.
Provide a brief plain text explanation (no markdown formatting, no asterisks or special characters).
Return ONLY the category name and explanation, nothing else."""},
            {"name": "action_item", "template": """Extract tasks from the email. Respond in JSON format only:
{ "task": "...", "deadline": "..." }.
Use plain text in the task field, no markdown formatting."""},
            {"name": "auto_reply", "template": """Draft a polite and professional reply to this email, incorporating user instructions.
Additionally, suggest 2-3 concise follow-up actions related to the email, and provide JSON metadata including the email's category and any extracted action items.
Respond in JSON format as follows:

{
    "body": "[The drafted email body]",
    "suggested_follow_ups": ["[Follow-up 1]", "[Follow-up 2]"],
    "metadata": {
        "category": "[Email Category]",
        "action_items": [{"task": "[Task 1]", "deadline": "[Deadline 1]"}]
    }
}"""},
        ]

        for prompt_data in default_prompts:
            existing_prompt = db.query(Prompt).filter(Prompt.name == prompt_data["name"]).first()
            if existing_prompt:
                if existing_prompt.template != prompt_data["template"]:
                    existing_prompt.template = prompt_data["template"]
                    db.commit()
                    print(f"Updating prompt: {prompt_data['name']}")
                else:
                    print(f"Prompt '{prompt_data['name']}' already up-to-date.")
            else:
                prompt = Prompt(name=prompt_data["name"], template=prompt_data["template"])
                db.add(prompt)
                db.commit()
                print(f"Seeding new prompt: {prompt_data['name']}")
    except Exception as e:
        db.rollback()
        print(f"Error seeding initial prompts: {e}")
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

