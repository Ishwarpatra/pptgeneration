"""
API Routes for Layout/Generation service.
The main entry point for end-to-end presentation generation.
"""
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import logging

from services.nlp.models import ContentExpansionRequest, PresentationOutline
from services.nlp.content_expander import ContentExpander
from services.style.presets import get_preset, list_presets
from .pptx_compiler import PPTXCompiler, generate_pptx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/generate", tags=["Generation"])


class FullGenerationRequest(BaseModel):
    """Request for end-to-end presentation generation."""
    topic: str = Field(description="Main topic for the presentation")
    num_slides: int = Field(default=5, ge=3, le=30)
    context: Optional[str] = Field(default=None, description="Additional context")
    style_id: str = Field(default="modern_minimal", description="Style preset ID")


class GenerationResponse(BaseModel):
    """Response with generation results."""
    success: bool
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    outline: Optional[dict] = None
    error: Optional[str] = None


@router.post("/presentation", response_model=GenerationResponse)
async def generate_presentation(request: FullGenerationRequest):
    """
    Generate a complete presentation end-to-end.
    
    1. Expands topic into structured outline (NLP Service)
    2. Applies style gene (Style Engine)
    3. Compiles to PPTX (Layout Engine)
    
    Returns the file path and download URL.
    """
    try:
        # Step 1: Content Expansion
        logger.info(f"Generating presentation for topic: {request.topic}")
        
        expander = ContentExpander()
        expansion_request = ContentExpansionRequest(
            topic=request.topic,
            num_slides=request.num_slides,
            context=request.context,
        )
        outline = await expander.expand_content(expansion_request)
        
        # Step 2: Get style
        try:
            style = get_preset(request.style_id)
        except ValueError:
            style = get_preset("modern_minimal")
        
        # Step 3: Compile PPTX
        compiler = PPTXCompiler(style=style)
        file_path = compiler.compile(outline)
        
        return GenerationResponse(
            success=True,
            file_path=file_path,
            download_url=f"/api/generate/download/{Path(file_path).name}",
            outline=outline.model_dump(),
        )
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return GenerationResponse(
            success=False,
            error=str(e),
        )


@router.get("/download/{filename}")
async def download_presentation(filename: str):
    """Download a generated presentation file."""
    file_path = Path("presentations") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


@router.post("/compile")
async def compile_from_outline(
    outline: PresentationOutline,
    style_id: str = "modern_minimal"
):
    """
    Compile a pre-generated outline to PPTX.
    Use this if you already have a structured outline.
    """
    try:
        file_path = generate_pptx(outline, style_id)
        return {
            "success": True,
            "file_path": file_path,
            "download_url": f"/api/generate/download/{Path(file_path).name}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check if Generation service is operational."""
    return {
        "status": "healthy",
        "service": "generation",
        "output_dir_exists": Path("presentations").exists(),
    }
