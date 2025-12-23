"""
API Routes for NLP/Content services.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging

from .models import ContentExpansionRequest, PresentationOutline
from .content_expander import ContentExpander, generate_presentation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/nlp", tags=["NLP"])


@router.post("/expand", response_model=PresentationOutline)
async def expand_content(request: ContentExpansionRequest):
    """
    Expand a topic into a full presentation outline.
    
    Takes a topic and optional parameters, returns a structured 
    presentation outline with slide specifications.
    """
    try:
        expander = ContentExpander()
        result = await expander.expand_content(request)
        return result
    except Exception as e:
        logger.error(f"Content expansion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate presentation outline: {str(e)}"
        )


@router.post("/quick-generate")
async def quick_generate(
    topic: str,
    num_slides: int = 5,
    style: str = None
):
    """
    Quick generation endpoint for simple use cases.
    """
    try:
        result = await generate_presentation(
            topic=topic,
            num_slides=num_slides,
            style=style
        )
        return result
    except Exception as e:
        logger.error(f"Quick generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check if NLP service is operational."""
    return {"status": "healthy", "service": "nlp"}
