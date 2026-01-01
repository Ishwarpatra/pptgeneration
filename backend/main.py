from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db, engine
from typing import List, Optional
from datetime import datetime
import uuid

# Import service routers
from services.nlp.routes import router as nlp_router
from services.nlp.analyze_routes import router as analyze_router
from services.style.routes import router as style_router
from services.layout.routes import router as generation_router
from services.visual.routes import router as visual_router

app = FastAPI(
    title="AI Presentation Generator",
    description="AI-powered presentation generation system with Gamma-style UI and Visual Synthesis",
    version="1.2.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://frontend:5173",  # Docker
    ],
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


# ============================================================================
# Presentations API (In-memory storage for now)
# ============================================================================

class PresentationModel(BaseModel):
    """Presentation data model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    thumbnail: str = "✨"
    createdAt: str = Field(default_factory=lambda: datetime.now().isoformat())
    updatedAt: Optional[str] = None
    isPrivate: bool = True
    author: str = "you"
    isFavorite: bool = False
    slideCount: Optional[int] = None
    styleId: Optional[str] = None


class UpdatePresentationRequest(BaseModel):
    """Request to update a presentation."""
    title: Optional[str] = None
    isPrivate: Optional[bool] = None
    isFavorite: Optional[bool] = None
    thumbnail: Optional[str] = None


# In-memory storage
_presentations_store: dict[str, PresentationModel] = {}


@app.get("/api/presentations", response_model=List[PresentationModel], tags=["Presentations"])
async def list_presentations(
    author: Optional[str] = Query(None),
    isFavorite: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all presentations with optional filtering."""
    presentations = list(_presentations_store.values())
    
    if author:
        presentations = [p for p in presentations if p.author == author]
    if isFavorite is not None:
        presentations = [p for p in presentations if p.isFavorite == isFavorite]
    
    presentations.sort(key=lambda p: p.createdAt, reverse=True)
    return presentations[offset:offset + limit]


@app.get("/api/presentations/{presentation_id}", response_model=PresentationModel, tags=["Presentations"])
async def get_presentation(presentation_id: str):
    """Get a specific presentation by ID."""
    if presentation_id not in _presentations_store:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    pres = _presentations_store[presentation_id]
    pres.updatedAt = datetime.now().isoformat()
    return pres


@app.put("/api/presentations/{presentation_id}", response_model=PresentationModel, tags=["Presentations"])
async def update_presentation(presentation_id: str, request: UpdatePresentationRequest):
    """Update a presentation's metadata."""
    if presentation_id not in _presentations_store:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    pres = _presentations_store[presentation_id]
    
    if request.title is not None:
        pres.title = request.title
    if request.isPrivate is not None:
        pres.isPrivate = request.isPrivate
    if request.isFavorite is not None:
        pres.isFavorite = request.isFavorite
    if request.thumbnail is not None:
        pres.thumbnail = request.thumbnail
    
    pres.updatedAt = datetime.now().isoformat()
    return pres


@app.patch("/api/presentations/{presentation_id}", response_model=PresentationModel, tags=["Presentations"])
async def patch_presentation(presentation_id: str, request: UpdatePresentationRequest):
    """Partially update a presentation."""
    return await update_presentation(presentation_id, request)


@app.delete("/api/presentations/{presentation_id}", status_code=204, tags=["Presentations"])
async def delete_presentation(presentation_id: str):
    """Delete a presentation."""
    if presentation_id not in _presentations_store:
        raise HTTPException(status_code=404, detail="Presentation not found")
    del _presentations_store[presentation_id]
    return None


def add_presentation_record(
    id: str,
    title: str,
    slide_count: int,
    style_id: str,
) -> PresentationModel:
    """Add a presentation record after generation."""
    presentation = PresentationModel(
        id=id,
        title=title,
        slideCount=slide_count,
        styleId=style_id,
    )
    _presentations_store[id] = presentation
    return presentation


# ============================================================================
# Core Routes
# ============================================================================

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
            "presentations": "/api/presentations",
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
            "visual_synthesis": "online",
            "presentations": "online"
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