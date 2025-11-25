# Email Summarizer

A prompt-driven email summarizer with a React (Vite) frontend and a FastAPI backend. This repo is configured for frontend deployment on Netlify and backend deployment on Render.

## Monorepo Layout
- Frontend: `emailsummarizer-main/emailsummarizer-main/frontend`
- Backend: `emailsummarizer-main/emailsummarizer-main/backend`

## Prerequisites
- Node.js 18+
- Python 3.10+

## Environment Variables

### Frontend (`.env`)
See `frontend/.env.example`:
- `VITE_API_BASE_URL` (default local: `http://localhost:8000`)

### Backend (`.env`)
See `backend/.env.example`:
- `GEMINI_API_KEY` (required for LLM features)
- `SUMMARY_PROMPT` (optional, default provided)
- `CATEGORY_PROMPT` (optional, default provided)
- `ACTION_ITEMS_PROMPT` (optional, default provided)
- `FRONTEND_ORIGIN` (CORS allow origin; local default: `http://localhost:5173`)

## Local Development

### Backend
1. `cd emailsummarizer-main/emailsummarizer-main/backend`
2. `pip install -r requirements.txt`
3. Create `.env` (copy from `.env.example`). Ensure `FRONTEND_ORIGIN` is set to `http://localhost:5173`.
4. Run: `python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

### Frontend
1. `cd emailsummarizer-main/emailsummarizer-main/frontend`
2. `npm install`
3. Create `.env` (copy from `.env.example`). For local backend use `VITE_API_BASE_URL=http://localhost:8000`.
4. Run: `npm run dev` (Vite defaults to `http://localhost:5173`)

## Usage
- Inbox: Fetch emails via `GET /emails`.
- Load Mock Inbox: Triggers `GET /emails/load-mock` (button in Inbox UI).
- Email Detail: View and process emails via `POST /emails/{id}/process`.
- Drafts: Manage via `/drafts` endpoints.
- Agent Chat: Interact via `POST /agent/chat`.
- Prompt Brain: View and update prompts via `GET/POST /prompts`.

## Deployment

### Netlify (Frontend)
- Netlify reads `netlify.toml`:
  - `base = "emailsummarizer-main/emailsummarizer-main/emailsummarizer-main/frontend"`
  - `command = "npm ci && npm run build"`
  - `publish = "dist"`
  - SPA redirects are configured.
- Set environment variable `VITE_API_BASE_URL` to your Render backend URL, e.g. `https://<render-service>.onrender.com`.

### Render (Backend)
- Render reads `render.yaml`:
  - Type: `web`, Env: `python`
  - `rootDir: emailsummarizer-main/emailsummarizer-main/emailsummarizer-main/backend`
  - `buildCommand: pip install -r requirements.txt`
  - `startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Env vars: `GEMINI_API_KEY`, optional prompt vars, `FRONTEND_ORIGIN` set to your Netlify domain (e.g. `https://<netlify-site>.netlify.app`).

## Notes
- CORS: Backend uses `FRONTEND_ORIGIN` to allow the frontend domain.
- Secrets: Do not commit API keys or `.env` files. `.gitignore` already excludes them.
- If your repository contains nested duplicates of frontend/backend, the generalized ignores will still exclude build artifacts and secrets.