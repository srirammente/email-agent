import os
import json
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the model if the key is present
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
else:
    model = None
    print("WARNING: No GEMINI_API_KEY found. LLM features will be disabled/mocked.")

class LLMService:
    def __init__(self):
        self.model = model

    async def generate_text(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback mock responses based on prompt type
            if 'Categorize' in prompt:
                return "Important"
            if 'Extract' in prompt:
                return "[\"Review the email\"]"
            if 'Draft' in prompt:
                return "Draft reply content based on instructions."
            if 'Context' in prompt:
                return "This is a mock answer to your query."
            print(f"LLM Error: {e}")
            return f"Error generating response: {e}"

    async def categorize_email(self, email_body: str, prompt_template: str) -> str:
        prompt = f"{prompt_template}\n\nEmail Body:\n{email_body}"
        return await self.generate_text(prompt)

    async def extract_action_items(self, email_body: str, prompt_template: str) -> list:
        prompt = f"{prompt_template}\n\nEmail Body:\n{email_body}"
        response_text = await self.generate_text(prompt)
        try:
            # Attempt to parse JSON from the response
            # Clean up potential markdown code blocks
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            parsed_json = json.loads(cleaned_text)
            # Ensure the parsed JSON is a list of dictionaries with 'task' and 'deadline'
            if isinstance(parsed_json, list) and all(
                isinstance(item, dict) and "task" in item and "deadline" in item
                for item in parsed_json
            ):
                return parsed_json
            else:
                print(f"Warning: LLM response for action items did not match expected JSON schema. Raw: {response_text}")
                return [] # Return empty list if schema is not as expected
        except json.JSONDecodeError:
            print(f"Warning: LLM response for action items was not valid JSON. Raw: {response_text}")
            return [] # Return empty list if JSON parsing fails
        except Exception as e:
            print(f"Unexpected error in extract_action_items: {e}. Raw: {response_text}")
            return []

    async def generate_draft(self, email_body: str, instructions: str, prompt_template: str, email_category: str = None, email_action_items: list = None) -> dict:
        """
        Generates an email draft, including suggested follow-ups and metadata,
        based on the email content, user instructions, and a structured prompt template.
        """
        from typing import Dict, Any
        
        # Enhance prompt with email's processed data for better context for draft generation
        context_for_prompt = f"Email Body:\n{email_body}\n"
        if email_category:
            context_for_prompt += f"Email Category: {email_category}\n"
        if email_action_items:
            context_for_prompt += f"Email Action Items: {json.dumps(email_action_items)}\n"

        full_prompt = f"{prompt_template}\n\nUser Instructions: {instructions}\n\n{context_for_prompt}"
        response_text = await self.generate_text(full_prompt)

        try:
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            parsed_draft = json.loads(cleaned_text)

            # Validate the structure of the parsed draft
            if isinstance(parsed_draft, dict) and \
               "body" in parsed_draft and \
               "suggested_follow_ups" in parsed_draft and \
               "metadata" in parsed_draft:
                return parsed_draft
            else:
                print(f"Warning: LLM draft response did not match expected JSON schema. Raw: {response_text}")
                # Fallback: create a basic dictionary if parsing fails but text is present
                return {
                    "body": response_text,
                    "suggested_follow_ups": [],
                    "metadata": {}
                }
        except json.JSONDecodeError:
            print(f"Warning: LLM draft response was not valid JSON. Raw: {response_text}")
            # Fallback: return a basic dictionary with raw text as body
            return {
                "body": response_text,
                "suggested_follow_ups": [],
                "metadata": {}
            }
        except Exception as e:
            print(f"Unexpected error in generate_draft: {e}. Raw: {response_text}")
            return {
                "body": response_text,
                "suggested_follow_ups": [],
                "metadata": {}
            }

    async def chat(self, query: str, context: str, history: list = [], focus_mode: bool = False) -> str:
        history_str = ""
        if history:
            history_str = "Conversation History:\n"
            for msg in history:
                role = "User" if msg.get("role") == "user" else "Agent"
                history_str += f"{role}: {msg.get('content')}\n"
            history_str += "\n"

        if focus_mode:
            # CONCISE MODE: For specific email discussions
            system_instruction = """
You are a helpful Email Productivity Agent. Your responses should be CONCISE and TO THE POINT.

CRITICAL FORMATTING RULES:
1. When user asks for action items ONLY, respond with JUST the action items in a bulleted list.
2. When user asks for a summary ONLY, respond with JUST a single paragraph summary (2-3 sentences max). NO bullet points, NO "Key points:" headers.
3. When user asks for specific information, provide ONLY that information.
4. Use proper markdown formatting with bullet points (•) for lists.
5. Keep responses SHORT and FOCUSED on what was asked.

RESPONSE FORMATS:

For "action items" or "action events" queries:
• [Action item 1]
• [Action item 2]
• [Action item 3]

For "summarize" queries:
[A single, continuous paragraph summarizing the email in 2-3 sentences. Do not use bullet points or headers.]

IMPORTANT:
- Do NOT repeat the entire email content unless specifically asked.
- Do NOT include unnecessary fields.
- Do NOT be verbose - be direct and concise.
- Use the conversation history to understand context.

Keep your answers SHORT, CLEAR, and HELPFUL.
"""
        else:
            # GENERAL MODE: For inbox overview and general questions
            system_instruction = """
You are a helpful Email Productivity Agent.
When answering questions about emails, always format the email details clearly and professionally.
Do not refer to emails as "Email 1" or "Email 2" in your final answer. Instead, use the email's subject or sender to identify it.
When listing or discussing specific emails, use a structured format with DOUBLE NEWLINES between fields to ensure clear separation:

**Subject:** [Subject]

**From:** [Sender]

**Date:** [Date]

**Summary:** [Summary]

**Action Items:** [List action items if any]

-------------------
Take the context of all the emails and keep it your memory
Then when asked regarding information in the email or draft
If asked spam important smth like pick the mails based on the categorization promt through which it is categorised
be consice with prompts when asked regarding information in the email or draft
If the user asks to perform an action (like "Draft a reply" or "Summarize this") without specifying an email, check the Conversation History.
If the user was just discussing a specific email, assume they are referring to that one.
Only ask for clarification if the context is truly ambiguous.
Also just give a sample draft reply for that email in the chat no need to redirect anywhere just a draft mail for mail 
now from the inbox just give me any deadlines or meeting to setup or attends just the dates...when asked something on a whole on the basis of inbox the formal shd be simple mail and task asked for like dates mention the dates and small contexts to and proper formatted sentnced content and the sender name shd be mentioned format in lines properly and make sure there is proper less spaving between each specification...Mention from email adress only 

Keep your answers concise and helpful.
"""

        prompt = f"{system_instruction}\n\nContext:\n{context}\n\n{history_str}User Query: {query}\n\nAnswer:"
        return await self.generate_text(prompt)

    async def summarize_email(self, email_body: str) -> str:
        prompt = f"Please provide a concise summary of the following email:\n\n{email_body}"
        return await self.generate_text(prompt)

llm_service = LLMService()
