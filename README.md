# AI Presentation Generator

An AI-powered presentation generation system with Gamma-style UI and Artbreeder-inspired visual synthesis.

## ✨ Features

- **🧠 NLP Content Expansion** - LLM-powered outline generation with structured output
- **🎨 Style Gene Engine** - Artbreeder-style theme breeding with LAB color interpolation
- **📊 Reference Analysis** - Extract styles from existing PPT files
- **📄 PPTX Compilation** - End-to-end PowerPoint generation with style application
- **🖥️ Gamma-Style UI** - Modern React frontend with block-based editing
- **📚 Template Library** - Pre-built templates and style presets
- **🖼️ Visual Synthesis** - AI image generation (DALL-E 3 / Stability AI) for slides

## 🚀 Quick Start

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
```env
DATABASE_URL=postgresql://user:password@localhost:5432/pptgen_db
MONGO_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your-openai-api-key-here
STABILITY_API_KEY=your-stability-api-key-here  # Optional
```

### 4. Run the Backend

```bash
cd backend
.\venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

### 6. Access the Application

- **Frontend UI**: http://localhost:5173
- **Swagger API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

| Service | Endpoint | Description |
|---------|----------|-------------|
| NLP | `/api/nlp/expand` | Expand topic to structured outline |
| Analysis | `/api/analyze/upload` | Extract style from reference PPT |
| Style | `/api/style/presets` | List style presets |
| Style | `/api/style/breed` | Mix two styles |
| Generate | `/api/generate/presentation` | Full end-to-end generation |
| Visual | `/api/visual/generate` | Generate AI images |
| Visual | `/api/visual/suggest` | Get image suggestions for slides |
| Visual | `/api/visual/styles` | List available image styles |

## 📁 Project Structure

```
pptgeneration/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── database.py          # PostgreSQL connection
│   └── services/
│       ├── nlp/             # Content expansion & analysis
│       ├── style/           # Style Gene engine
│       ├── layout/          # PPTX compiler
│       └── visual/          # AI Image generation
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main application
│   │   ├── components/      # React components
│   │   │   ├── BlockEditor/ # Block-based slide editor + Image Generator
│   │   │   └── Templates/   # Template gallery
│   │   └── index.css        # Global styles
│   └── package.json
└── docker-compose.yml       # Database services
```

## 🛠️ Development Phases

- [x] Phase 1-4: Core Backend Services
- [x] Phase 5: Reference Analysis
- [x] Phase 6: Frontend UI + Block Editor + Template Library + Visual Synthesis
- [ ] Phase 7: Real-time Collaboration & Export Options
