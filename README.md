# Email Summarizer Agent

An AI-powered email productivity assistant with intelligent categorization, action item extraction, and automated draft generation. Built with React (Vite) frontend and FastAPI backend, powered by Google's Gemini 2.0 Flash.

## 📋 Table of Contents
- [System Design](#-system-design)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Setup](#-setup)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)

---

## 🏗️ System Design

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React + Vite SPA]
        Router[React Router]
        Components[UI Components]
    end
    
    subgraph "Backend Layer"
        API[FastAPI Server]
        CORS[CORS Middleware]
        Routes[API Routes]
    end
    
    subgraph "Business Logic"
        Store[Data Store]
        LLM[LLM Service]
        Auth[Gmail Auth]
    end
    
    subgraph "Data Layer"
        DB[(SQLite Database)]
        Mock[Mock Data]
    end
    
    subgraph "External Services"
        Gemini[Google Gemini API]
        Gmail[Gmail API]
    end
    
    UI --> Router --> Components
    Components --> |HTTP/REST| CORS
    CORS --> API
    API --> Routes
    Routes --> Store
    Routes --> LLM
    Routes --> Auth
    Store --> DB
    LLM --> Gemini
    Auth --> Gmail
    Mock -.-> Store
    
    style Gemini fill:#4285f4
    style Gmail fill:#ea4335
    style DB fill:#34a853
```

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant FastAPI
    participant LLM Service
    participant Database
    participant Gemini API
    
    User->>Frontend: Open Inbox
    Frontend->>FastAPI: GET /emails
    FastAPI->>Database: Query emails
    Database-->>FastAPI: Email records
    FastAPI-->>Frontend: Email list (JSON)
    Frontend-->>User: Display emails
    
    User->>Frontend: Click "Process Email"
    Frontend->>FastAPI: POST /emails/{id}/process
    FastAPI->>LLM Service: categorize_email()
    LLM Service->>Gemini API: Categorization prompt
    Gemini API-->>LLM Service: Category result
    FastAPI->>LLM Service: extract_action_items()
    LLM Service->>Gemini API: Action items prompt
    Gemini API-->>LLM Service: Action items (JSON)
    FastAPI->>LLM Service: summarize_email()
    LLM Service->>Gemini API: Summary prompt
    Gemini API-->>LLM Service: Summary text
    FastAPI->>Database: Update email record
    Database-->>FastAPI: Success
    FastAPI-->>Frontend: Processing complete
    Frontend-->>User: Show processed email
```

### Data Flow Architecture

```mermaid
%% Updated diagram with better color visibility
flowchart LR
    subgraph "Input Sources"
        Gmail[Gmail API]
        Mock[Mock JSON]
    end
    
    subgraph "Processing Pipeline"
        Ingest[Email Ingestion]
        Parse[Email Parser]
        Queue[Background Tasks]
        
        subgraph "AI Processing"
            Cat[Categorization]
            Act[Action Items]
            Sum[Summarization]
        end
        
        Draft[Draft Generation]
    end
    
    subgraph "Storage"
        EmailDB[(Emails Table)]
        DraftDB[(Drafts Table)]
        PromptDB[(Prompts Table)]
    end
    
    subgraph "Output"
        UI[User Interface]
        Chat[Agent Chat]
    end
    
    Gmail --> Ingest
    Mock --> Ingest
    Ingest --> Parse
    Parse --> Queue
    Queue --> Cat
    Queue --> Act
    Queue --> Sum
    Cat --> EmailDB
    Act --> EmailDB
    Sum --> EmailDB
    EmailDB --> UI
    EmailDB --> Draft
    Draft --> DraftDB
    DraftDB --> UI
    PromptDB --> Cat
    PromptDB --> Act
    PromptDB --> Draft
    EmailDB --> Chat
    
    style Cat fill:#ff9800,stroke:#333,stroke-width:2px,color:#000
    style Act fill:#ff9800,stroke:#333,stroke-width:2px,color:#000
    style Sum fill:#ff9800,stroke:#333,stroke-width:2px,color:#000
    style Draft fill:#ff9800,stroke:#333,stroke-width:2px,color:#000
```

### Database Schema

```mermaid
erDiagram
    EMAILS ||--o{ DRAFTS : "generates"
    EMAILS {
        string id PK
        string sender
        string subject
        text body
        datetime timestamp
        boolean read
        string category
        json action_items
        text summary
        boolean processed
    }
    
    DRAFTS {
        int id PK
        string email_id FK
        string subject
        text body
        json suggested_follow_ups
        json draft_metadata
    }
    
    PROMPTS {
        int id PK
        string prompt_type UK
        text prompt_text
    }
```

---

## ✨ Features

### 🎯 Core Capabilities
- **Smart Email Categorization**: Auto-categorize emails (Important, Spam, Promotional, etc.)
- **Action Item Extraction**: Automatically extract tasks and deadlines from emails
- **AI Summarization**: Generate concise summaries of lengthy emails
- **Intelligent Draft Generation**: Create context-aware email replies with suggested follow-ups
- **Conversational Agent**: Context-aware chatbot for inbox queries and email assistance
- **Prompt Brain**: Customize AI behavior by editing system prompts

### 🔄 Workflows
1. **Email Processing**: Gmail sync → Parse → Background AI processing
2. **Draft Creation**: Email selection → AI draft generation → User editing → Save
3. **Agent Interaction**: Inbox context + specific email + conversation history → LLM response

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **Vite** | Build tool & dev server |
| **React Router v6** | Client-side routing |
| **Axios** | HTTP client |
| **CSS3** | Styling |

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **SQLAlchemy** | ORM for database |
| **SQLite** | Lightweight database |
| **Pydantic** | Data validation |
| **Google Generative AI** | Gemini 2.0 Flash integration |
| **Gmail API** | Email fetching |

### Infrastructure
- **Netlify**: Frontend hosting (SPA deployment)
- **Render**: Backend hosting (Python web service)
- **Git**: Version control

---

## 🏛️ Architecture

### Monorepo Structure
```
emailsummarizer-main/
├── emailsummarizer-main/
│   ├── frontend/              # React application
│   │   ├── src/
│   │   │   ├── components/   # Inbox, EmailDetail, DraftEditor, etc.
│   │   │   ├── App.jsx       # Main app component
│   │   │   └── config.js     # API configuration
│   │   ├── public/
│   │   ├── package.json
│   │   └── vite.config.js
│   └── backend/              # FastAPI application
│       ├── main.py           # API routes
│       ├── llm.py            # Gemini AI integration
│       ├── store.py          # Data access layer
│       ├── database.py       # SQLAlchemy models
│       ├── auth.py           # Gmail OAuth
│       ├── mock_data/        # Test data
│       └── requirements.txt
├── netlify.toml
├── render.yaml
└── README.md
```

### Key Backend Modules

| Module | Responsibility |
|--------|---------------|
| `main.py` | API endpoints, CORS, background tasks |
| `llm.py` | Gemini API wrapper, prompt engineering |
| `store.py` | Database operations (CRUD) |
| `database.py` | SQLAlchemy models and DB setup |
| `auth.py` | Gmail API authentication |

### Frontend Architecture

```mermaid
graph LR
    App[App.jsx] --> Layout
    Layout --> Inbox
    Layout --> EmailDetail
    Layout --> DraftList
    Layout --> DraftEditor
    Layout --> AgentChat
    Layout --> PromptBrain
    
    Inbox --> |GET /emails<br/>GET /emails/load-mock<br/>GET /gmail/sync| Backend[FastAPI]
    EmailDetail --> |GET /emails/:id<br/>POST /emails/:id/process<br/>POST /drafts| Backend
    DraftList --> |GET /drafts| Backend
    DraftEditor --> |GET /drafts/:id<br/>PUT /drafts/:id<br/>DELETE /drafts/:id| Backend
    AgentChat --> |POST /agent/chat| Backend
    PromptBrain --> |GET /prompts<br/>POST /prompts| Backend
```


---

## 🚀 Setup

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.10+
- **Google Cloud Account** (for Gemini API key)

### Environment Variables

#### Frontend `.env`
```env
VITE_API_BASE_URL=http://localhost:8000
```

#### Backend `.env`
```env
GEMINI_API_KEY=your_gemini_api_key_here
FRONTEND_ORIGIN=http://localhost:5173
SUMMARY_PROMPT=Please provide a concise summary...
CATEGORY_PROMPT=Categorize this email as...
ACTION_ITEMS_PROMPT=Extract action items as JSON...
```

### Local Development

#### 1. Backend Setup
```bash
cd emailsummarizer-main/emailsummarizer-main/backend
pip install -r requirements.txt
cp .env.example .env  # Then edit .env with your keys
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will run at `http://localhost:8000`

#### 2. Frontend Setup
```bash
cd emailsummarizer-main/emailsummarizer-main/frontend
npm install
cp .env.example .env  # Then edit .env
npm run dev
```

Frontend will run at `http://localhost:5173`

---

## 📡 API Documentation

### Email Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/emails` | Fetch all emails |
| `GET` | `/emails/{email_id}` | Get single email |
| `GET` | `/emails/load-mock` | Load mock inbox data |
| `GET` | `/gmail/sync` | Sync from Gmail API |
| `POST` | `/emails/{email_id}/process` | Trigger AI processing |

### Draft Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/drafts` | List all drafts |
| `GET` | `/drafts/{draft_id}` | Get single draft |
| `POST` | `/drafts` | Generate new draft |
| `PUT` | `/drafts/{draft_id}` | Update draft |
| `DELETE` | `/drafts/{draft_id}` | Delete draft |

### Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/agent/chat` | Chat with AI agent |
| `GET` | `/prompts` | Get all system prompts |
| `POST` | `/prompts` | Update prompts |

### Example Request: Generate Draft
```bash
curl -X POST http://localhost:8000/drafts \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "abc123",
    "instructions": "Write a polite decline"
  }'


```

**Response:**
```json
{
  "id": 1,
  "subject": "Re: Meeting Request",
  "body": "Thank you for reaching out...",
  "suggested_follow_ups": [
    "Schedule a follow-up call",
    "Send calendar availability"
  ],
  "metadata": {
    "tone": "professional",
    "confidence": 0.92
  }
}
```

---

## 🌐 Deployment

### Netlify (Frontend)

**Configuration:** `netlify.toml`
```toml
[build]
  base = "emailsummarizer-main/emailsummarizer-main/frontend"
  command = "npm ci && npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Environment Variables:**
- `VITE_API_BASE_URL`: Your Render backend URL (e.g., `https://your-app.onrender.com`)

### Render (Backend)

**Configuration:** `render.yaml`
```yaml
services:
  - type: web
    name: email-agent-backend
    env: python
    rootDir: emailsummarizer-main/emailsummarizer-main/backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: FRONTEND_ORIGIN
        value: https://your-netlify-site.netlify.app
```

**Environment Variables:**
- `GEMINI_API_KEY`: Your Google Gemini API key
- `FRONTEND_ORIGIN`: Your Netlify frontend URL

### Deployment Workflow

```mermaid
flowchart TD
    Push[Git Push] --> GitHub[GitHub Repo]
    GitHub --> |Auto Deploy| Netlify[Netlify Build]
    GitHub --> |Auto Deploy| Render[Render Build]
    
    Netlify --> |npm ci && build| NetDist[dist/ folder]
    NetDist --> NetServe[Serve SPA]
    
    Render --> |pip install| RenderDeps[Install Dependencies]
    RenderDeps --> RenderStart[Start Uvicorn]
    
    NetServe --> |CORS Request| RenderStart
    
    style Netlify fill:#5e72e4,stroke:#333,stroke-width:2px,color:#fff
    style Render fill:#2dce89,stroke:#333,stroke-width:2px,color:#fff
```

---

## 📝 Notes

- **CORS**: Backend uses `FRONTEND_ORIGIN` environment variable for CORS configuration
- **Secrets**: Never commit `.env` files or API keys (already in `.gitignore`)
- **Database**: SQLite file (`email_agent.db`) is created automatically on first run
- **Background Tasks**: Email processing runs asynchronously using FastAPI's `BackgroundTasks`
- **Mock Data**: Use `/emails/load-mock` for testing without Gmail authentication

---

## 🤝 Contributing

This project is a demonstration of modern full-stack development with AI integration. Feel free to fork and enhance!