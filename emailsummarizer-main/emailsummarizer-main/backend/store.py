from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database import Email, Prompt, Draft # Import the models we defined

class Store:
    def __init__(self, db: Session):
        self.db = db

    def get_emails(self) -> List[Email]:
        return self.db.query(Email).all()

    def get_email(self, email_id: str) -> Optional[Email]:
        return self.db.query(Email).filter(Email.id == email_id).first()

    def add_emails(self, new_emails: List[Dict]):
        for email_data in new_emails:
            existing_email = self.db.query(Email).filter(Email.id == email_data["id"]).first()
            if not existing_email:
                email = Email(**email_data)
                self.db.add(email)
        self.db.commit()

    def update_email(self, email_id: str, updates: Dict) -> Optional[Email]:
        email = self.db.query(Email).filter(Email.id == email_id).first()
        if email:
            for key, value in updates.items():
                setattr(email, key, value)
            self.db.commit()
            self.db.refresh(email) # Refresh the object to get latest state from DB
            return email
        return None

    def get_prompts(self) -> Dict[str, str]:
        prompts = self.db.query(Prompt).all()
        return {p.name: p.template for p in prompts}

    def update_prompts(self, new_prompts: Dict) -> Dict[str, str]:
        for prompt_name, prompt_template in new_prompts.items():
            prompt = self.db.query(Prompt).filter(Prompt.name == prompt_name).first()
            if prompt:
                prompt.template = prompt_template
            else:
                new_prompt = Prompt(name=prompt_name, template=prompt_template)
                self.db.add(new_prompt)
        self.db.commit()
        return self.get_prompts()

    def get_drafts(self) -> List[Draft]:
        return self.db.query(Draft).all()

    def save_draft(self, draft_data: Dict) -> Draft:
        draft = Draft(**draft_data)
        self.db.add(draft)
        self.db.commit()
        self.db.refresh(draft)
        return draft

    def update_draft(self, draft_id: int, updates: Dict) -> Optional[Draft]:
        draft = self.db.query(Draft).filter(Draft.id == draft_id).first()
        if draft:
            for key, value in updates.items():
                setattr(draft, key, value)
            self.db.commit()
            self.db.refresh(draft)
            return draft
        return None

    def get_draft(self, draft_id: int) -> Optional[Draft]:
        return self.db.query(Draft).filter(Draft.id == draft_id).first()

    def delete_draft(self, draft_id: int) -> bool:
        draft = self.db.query(Draft).filter(Draft.id == draft_id).first()
        if draft:
            self.db.delete(draft)
            self.db.commit()
            return True
        return False
