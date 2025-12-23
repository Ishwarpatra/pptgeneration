# AI Presentation Generator

An AI-powered presentation generation system with Gamma-style UI and Artbreeder-inspired visual synthesis.

## Features

- **NLP Content Expansion** - LLM-powered outline generation with structured output
- **Style Gene Engine** - Artbreeder-style theme breeding with LAB color interpolation
- **Reference Analysis** - Extract styles from existing PPT files
- **PPTX Compilation** - End-to-end PowerPoint generation with style application

## Quick Start

### 1. Start Docker Services

```bash
docker-compose up -d
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Configure Environment

Create `backend/.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/pptgen_db
MONGO_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your-openai-api-key-here
```

### 4. Run the Server

```bash
cd backend
.\venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Access the API

- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

| Service | Endpoint | Description |
|---------|----------|-------------|
| NLP | `/api/nlp/expand` | Expand topic to structured outline |
| Analysis | `/api/analyze/upload` | Extract style from reference PPT |
| Style | `/api/style/presets` | List style presets |
| Style | `/api/style/breed` | Mix two styles |
| Generate | `/api/generate/presentation` | Full end-to-end generation |

## Project Structure

```
pptgeneration/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── database.py          # PostgreSQL connection
│   └── services/
│       ├── nlp/             # Content expansion & analysis
│       ├── style/           # Style Gene engine
│       └── layout/          # PPTX compiler
├── docker-compose.yml       # Database services
└── frontend/                # (Coming soon)
```
