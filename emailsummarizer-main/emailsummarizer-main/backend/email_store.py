import json
from pathlib import Path
from typing import List, Dict

# Define the path to the JSON file where emails will be stored
EMAIL_STORAGE_FILE = Path(__file__).parent / "stored_emails.json"

def load_emails() -> List[Dict]:
    """Loads all stored emails from the JSON file."""
    if not EMAIL_STORAGE_FILE.exists():
        return []
    with open(EMAIL_STORAGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_emails(emails: List[Dict]):
    """Saves a list of emails to the JSON file."""
    with open(EMAIL_STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(emails, f, indent=4)

def add_email(email_data: Dict):
    """Adds a single email to the store, updating if an email with the same ID exists."""
    emails = load_emails()
    updated = False
    for i, email in enumerate(emails):
        if email.get("id") == email_data.get("id"):
            emails[i] = email_data
            updated = True
            break
    if not updated:
        emails.append(email_data)
    save_emails(emails)

def get_email_by_id(email_id: str) -> Dict | None:
    """Retrieves a single email by its ID."""
    emails = load_emails()
    for email in emails:
        if email.get("id") == email_id:
            return email
    return None

def clear_emails():
    """Clears all stored emails from the JSON file."""
    if EMAIL_STORAGE_FILE.exists():
        EMAIL_STORAGE_FILE.unlink()
    print("Cleared all stored emails.")