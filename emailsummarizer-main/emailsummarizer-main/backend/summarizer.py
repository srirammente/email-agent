from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from typing import Optional
import threading

class ModelManager:
    _instance: Optional['ModelManager'] = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.model_name = "google/pegasus-xsum"
        self.is_initialized = False
    
    @classmethod
    def get_instance(cls) -> 'ModelManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def initialize(self):
        if not self.is_initialized:
            with self._lock:
                if not self.is_initialized:
                    print(f"Initializing Pegasus model ({self.model_name})... This might take a moment.")
                    self.tokenizer = PegasusTokenizer.from_pretrained(self.model_name)
                    self.model = PegasusForConditionalGeneration.from_pretrained(self.model_name)
                    self.is_initialized = True
                    print("Pegasus model initialized.")
                else:
                    print("Model already initialized.")
        else:
            print("Model already initialized.")

# Global functions that use the singleton
def initialize_model():
    """Initialize the model using the singleton pattern"""
    manager = ModelManager.get_instance()
    manager.initialize()

def summarize_email(subject: str, sender: str, snippet: str, body: str) -> str:
    """Summarize an email using the singleton model manager"""
    manager = ModelManager.get_instance()
    manager.initialize()  # Safe to call, won't reinitialize if already done
    
    full_text = f"Summarize this email casually:\nSubject: {subject}\nFrom: {sender}\nSnippet: {snippet}\n\n{body}"
    tokens = manager.tokenizer(full_text, truncation=True, padding="longest", return_tensors="pt", max_length=512)
    summary_ids = manager.model.generate(
        tokens["input_ids"],
        max_length=150,
        min_length=40,
        num_beams=4,
        early_stopping=True
    )
    summary = manager.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary
