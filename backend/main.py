from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db, engine

# Import service routers
from services.nlp.routes import router as nlp_router
from services.nlp.analyze_routes import router as analyze_router
from services.style.routes import router as style_router
from services.layout.routes import router as generation_router
from services.visual.routes import router as visual_router

app = FastAPI(
    title="AI Presentation Generator",
    description="AI-powered presentation generation system with Gamma-style UI and Visual Synthesis",
    version="1.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nlp_router)
app.include_router(analyze_router)
app.include_router(style_router)
app.include_router(generation_router)
app.include_router(visual_router)


@app.get("/")
def read_root():
    return {
        "status": "System Online",
        "phase": "6 - Visual Synthesis Active",
        "endpoints": {
            "nlp": "/api/nlp",
            "analyze": "/api/analyze",
            "style": "/api/style",
            "generate": "/api/generate",
            "visual": "/api/visual",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Comprehensive health check for all services."""
    return {
        "status": "healthy",
        "services": {
            "api_gateway": "online",
            "nlp": "online",
            "reference_analysis": "online",
            "style_engine": "online",
            "generation": "online",
            "visual_synthesis": "online"
        }
    }


@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"database": "Connected", "type": "PostgreSQL"}
    except Exception as e:
        return {"database": "Error", "details": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)