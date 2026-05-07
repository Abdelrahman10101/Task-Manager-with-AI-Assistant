# 🗂️ TaskFlow — Mini Task Manager

A full-stack task management app with AI-powered project summaries.

## Stack
- **Frontend**: Vite + React, Vanilla CSS
- **Backend**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **AI**: HuggingFace Inference API (Mistral-7B)

---

## Setup

### 1. PostgreSQL
Create a database named `taskmanager`:
```sql
CREATE DATABASE taskmanager;
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt

# Edit .env with your DB credentials and HF token
# Then run:
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

App runs at: http://localhost:5173

---

## Environment Variables

**backend/.env**
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/taskmanager
SECRET_KEY=your-super-secret-key
HF_TOKEN=hf_your_huggingface_token   # optional, get free at huggingface.co/settings/tokens
```

**frontend/.env**
```
VITE_API_URL=http://localhost:8000
```

---

## Features
- ✅ JWT Authentication (register/login)
- ✅ Project CRUD with color coding
- ✅ Task CRUD with Kanban board (To Do / In Progress / Done)
- ✅ Priority badges (Low / Medium / High)
- ✅ AI Project Summarizer (HuggingFace Mistral-7B)
- ✅ AI Task Suggester
- ✅ Data isolation (users only see their own data)
- ✅ Responsive dark UI
