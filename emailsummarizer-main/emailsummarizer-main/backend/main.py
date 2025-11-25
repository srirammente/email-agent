from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import base64
import re
import json
from datetime import datetime
import os # Added for load_mock_emails
from sqlalchemy.orm import Session

from store import Store
from llm import llm_service
from auth import get_gmail_service
from database import get_db, create_db_tables, seed_initial_prompts, Email, Prompt, Draft # Import new database functions and models

app = FastAPI(title="Prompt-Driven Email Agent")

# CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event for database connection and seeding
@app.on_event("startup")
def startup_db_client():
    create_db_tables() # Create tables if they don't exist
    seed_initial_prompts() # Seed initial prompts

# Models
class PromptUpdate(BaseModel):
    categorization: Optional[str] = None
    action_item: Optional[str] = None
    auto_reply: Optional[str] = None

class ChatRequest(BaseModel):
    query: str
    email_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = []

class DraftResponse(BaseModel):
    id: int
    subject: str
    body: str
    suggested_follow_ups: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class DraftRequest(BaseModel):
    email_id: str
    instructions: Optional[str] = "Reply to this email"

class DraftUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    suggested_follow_ups: Optional[List[str]] = None
    draft_metadata: Optional[Dict[str, Any]] = None

# Helper to parse Gmail message
def parse_gmail_message(msg):
    payload = msg.get('payload', {})
    headers = payload.get('headers', [])
    
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
    
    # Get Body
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                body_data = part['body'].get('data')
                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                    break
    elif 'body' in payload and 'data' in payload['body']:
        body_data = payload['body'].get('data')
        if body_data:
            body = base64.urlsafe_b64decode(body_data).decode('utf-8')
    
    if not body:
        body = msg.get('snippet', '')

    return {
        "id": msg['id'],
        "sender": sender,
        "subject": subject,
        "body": body,
        "timestamp": datetime.now(), # Use datetime object for SQLAlchemy
        "read": 'UNREAD' not in msg.get('labelIds', [])
    }

async def process_email_background(email_id: str):
    db = next(get_db()) # Get a new session for background task
    _store = Store(db)
    email = _store.get_email(email_id)
    if not email:
        print(f"Email {email_id} not found for background processing. It might have been deleted.")
        db.close()
        return

    prompts = _store.get_prompts() # Get prompts from the database
    categorization_prompt = prompts.get("categorization", "Default categorization prompt if not found.")
    action_item_prompt = prompts.get("action_item", "Default action item prompt if not found.")

    try:
        category = await llm_service.categorize_email(email.body, categorization_prompt)
        raw_actions = await llm_service.extract_action_items(email.body, action_item_prompt)
        summary = await llm_service.summarize_email(email.body)

        action_items_parsed = []
        if isinstance(raw_actions, list):
            action_items_parsed = raw_actions
        elif isinstance(raw_actions, str):
            try:
                action_items_parsed = json.loads(raw_actions)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse action items for email {email_id}. Raw: {raw_actions}")
                action_items_parsed = []
        
        updates = {
            "category": category.strip(),
            "action_items": action_items_parsed,
            "summary": summary,
            "processed": True
        }
        
        _store.update_email(email_id, updates)
        print(f"Email {email_id} processed successfully. Category: {category.strip()}")

    except Exception as e:
        print(f"Error processing email {email_id}: {e}")
        _store.update_email(email_id, {"processed": False, "processing_error": str(e)})
    finally:
        db.close()

# Endpoints

@app.get("/emails")
async def get_emails(db: Session = Depends(get_db)):
    _store = Store(db)
    emails = _store.get_emails()
    # Convert SQLAlchemy models to dicts for JSON serialization
    return [{"id": e.id, "sender": e.sender, "subject": e.subject, "body": e.body, 
             "timestamp": e.timestamp.isoformat() if e.timestamp else None, 
             "read": e.read, "category": e.category, "action_items": e.action_items, 
             "summary": e.summary, "processed": e.processed} for e in emails]

@app.get("/gmail/sync")
async def sync_gmail(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])
        
        new_emails_data = []
        _store = Store(db)

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            parsed_email_data = parse_gmail_message(msg)
            new_emails_data.append(parsed_email_data)
        
        _store.add_emails(new_emails_data)

        for email_data in new_emails_data:
            background_tasks.add_task(process_email_background, email_data["id"])
        
        return {"status": "success", "count": len(new_emails_data)}
    except Exception as e:
        print(f"Gmail Sync Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emails/load-mock")
async def load_mock_emails(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Load mock emails from mock_data/inbox.json for testing without Gmail auth"""
    try:
        mock_file = os.path.join(os.path.dirname(__file__), "mock_data", "inbox.json")
        if not os.path.exists(mock_file):
            raise HTTPException(status_code=404, detail="Mock data file not found")
        
        with open(mock_file, 'r', encoding='utf-8') as f:
            mock_emails_data = json.load(f)
        
        _store = Store(db)
        # Convert timestamp strings to datetime objects
        for email_data in mock_emails_data:
            if "timestamp" in email_data and isinstance(email_data["timestamp"], str):
                try:
                    email_data["timestamp"] = datetime.fromisoformat(email_data["timestamp"].replace('Z', '+00:00'))
                except ValueError:
                    print(f"Warning: Could not parse timestamp {email_data['timestamp']}. Using current time.")
                    email_data["timestamp"] = datetime.now()
        _store.add_emails(mock_emails_data)
        
        for email_data in mock_emails_data:
            background_tasks.add_task(process_email_background, email_data["id"])
        
        return {"status": "success", "count": len(mock_emails_data)}
    except Exception as e:
        print(f"Load Mock Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emails/{email_id}")
async def get_email(email_id: str, db: Session = Depends(get_db)):
    _store = Store(db)
    email = _store.get_email(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    # Convert SQLAlchemy model to dict for JSON serialization
    return {"id": email.id, "sender": email.sender, "subject": email.subject, "body": email.body, 
            "timestamp": email.timestamp.isoformat() if email.timestamp else None, 
            "read": email.read, "category": email.category, "action_items": email.action_items, 
            "summary": email.summary, "processed": email.processed}

@app.post("/emails/{email_id}/process")
async def process_email(
    email_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    _store = Store(db)
    email = _store.get_email(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    background_tasks.add_task(process_email_background, email_id)
    return {"status": "processing started", "email_id": email_id}

@app.get("/prompts", response_model=Dict[str, str]) # Specify response model
async def get_prompts(db: Session = Depends(get_db)):
    _store = Store(db)
    return _store.get_prompts()

@app.post("/prompts")
async def update_prompts(prompts: PromptUpdate, db: Session = Depends(get_db)):
    _store = Store(db)
    updates = prompts.dict(exclude_unset=True)
    _store.update_prompts(updates)
    return _store.get_prompts()

@app.post("/agent/chat", response_model=Dict[str, str]) # Specify response model
async def agent_chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    _store = Store(db)
    
    # 1. Build Global Context (Inbox Overview)
    # Fetch recent emails (e.g., last 20) to provide general context
    all_emails = _store.get_emails()
    # Sort by timestamp desc to ensure "latest" is actually latest
    all_emails.sort(key=lambda x: x.timestamp if x.timestamp else datetime.min, reverse=True)
    
    recent_emails = all_emails[:20] # Limit to 20 for context window
    
    inbox_context_parts = ["📬 **INBOX OVERVIEW** (Most Recent First)\n"]
    for i, email in enumerate(recent_emails):
        if i < 5:
            # Full details for top 5 emails
            items_str = ""
            if email.action_items:
                if isinstance(email.action_items, list):
                    if email.action_items and isinstance(email.action_items[0], dict):
                         items_str = "\n  • " + "\n  • ".join([item.get('task', '') for item in email.action_items])
                    else:
                         items_str = "\n  • " + "\n  • ".join([str(item) for item in email.action_items])
            
            email_detail = f"\n📧 **Email #{i+1}**\n" \
                           f"**From:** {email.sender}\n" \
                           f"**Subject:** {email.subject}\n" \
                           f"**Date:** {email.timestamp}\n" \
                           f"**Category:** {email.category or 'Uncategorized'}\n"
            
            if email.summary:
                email_detail += f"**Summary:** {email.summary}\n"
            
            if items_str:
                email_detail += f"**Action Items:**{items_str}\n"
            
            email_detail += f"\n**Full Body:**\n{email.body}\n" \
                           f"{'─' * 50}\n"
            inbox_context_parts.append(email_detail)
        else:
            # Summary for older emails
            email_summary = f"\n📨 **Email #{i+1}:** {email.subject}\n" \
                           f"   From: {email.sender} | Date: {email.timestamp}"
            if email.category:
                email_summary += f" | Category: {email.category}"
            if email.summary:
                email_summary += f"\n   Summary: {email.summary}"
            
            inbox_context_parts.append(email_summary)
    
    inbox_context = "\n".join(inbox_context_parts)

    # 2. Build Specific Context (if email_id provided)
    specific_context = ""
    if request.email_id:
        email = _store.get_email(request.email_id)
        if email:
            items_str = "None"
            if email.action_items:
                if isinstance(email.action_items, list):
                    if email.action_items and isinstance(email.action_items[0], dict):
                         items_str = "\n  • " + "\n  • ".join([item.get('task', '') for item in email.action_items])
                    else:
                         items_str = "\n  • " + "\n  • ".join([str(item) for item in email.action_items])

            specific_context = f"\n\nUser is currently viewing this specific email:\n" \
                               f"Subject: {email.subject}\n" \
                               f"Sender: {email.sender}\n" \
                               f"Date: {email.timestamp}\n" \
                               f"Body: {email.body}\n" \
                               f"Category: {email.category}\n" \
                               f"Summary: {email.summary}\n" \
                               f"Action Items: {items_str}\n"

    # 3. Combine Context
    full_context = inbox_context + specific_context
    
    # 4. Call LLM
    # The LLM now has visibility into the inbox, specific email, and conversation history.
    response = await llm_service.chat(request.query, full_context, request.history)
    return {"response": response}

@app.post("/drafts", response_model=DraftResponse) # Add response_model for structured output
async def generate_draft(
    request: DraftRequest,
    db: Session = Depends(get_db)
):
    _store = Store(db)
    email = _store.get_email(request.email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    prompts = _store.get_prompts()
    auto_reply_prompt = prompts.get("auto_reply", "Default auto-reply prompt if not found.")

    # Pass email's processed data to generate_draft for better context
    draft_output = await llm_service.generate_draft(
        email_body=email.body,
        instructions=request.instructions,
        prompt_template=auto_reply_prompt,
        email_category=email.category,
        email_action_items=email.action_items
    )
    
    draft_data = {
        "email_id": request.email_id,
        "subject": f"Re: {email.subject}",
        "body": draft_output.get("body", ""),
        "suggested_follow_ups": draft_output.get("suggested_follow_ups", []),
        "draft_metadata": draft_output.get("metadata", {})  # Map to draft_metadata column
    }
    saved_draft = _store.save_draft(draft_data)
    
    # Return the saved draft data, ensuring it matches DraftResponse model
    return DraftResponse(
        id=saved_draft.id,
        subject=saved_draft.subject,
        body=saved_draft.body,
        suggested_follow_ups=saved_draft.suggested_follow_ups,
        metadata=saved_draft.draft_metadata  # Map from draft_metadata column
    )

@app.get("/drafts")
async def get_drafts(db: Session = Depends(get_db)):
    _store = Store(db)
    drafts = _store.get_drafts()
    return drafts

@app.get("/drafts/{draft_id}")
async def get_draft(draft_id: int, db: Session = Depends(get_db)):
    _store = Store(db)
    draft = _store.get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft

@app.put("/drafts/{draft_id}")
async def update_draft(
    draft_id: int,
    updates: DraftUpdate,
    db: Session = Depends(get_db)
):
    _store = Store(db)
    updated_draft = _store.update_draft(draft_id, updates.dict(exclude_unset=True))
    if not updated_draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return updated_draft

@app.delete("/drafts/{draft_id}")
async def delete_draft(draft_id: int, db: Session = Depends(get_db)):
    _store = Store(db)
    success = _store.delete_draft(draft_id)
    if not success:
        raise HTTPException(status_code=404, detail="Draft not found")
    return {"status": "deleted", "draft_id": draft_id}
