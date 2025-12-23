"""
API Routes for Visual Synthesis Service.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import base64
import logging

from .image_generator import (
    ImageGenerator,
    ImageSize,
    ImageStyle,
    GeneratedImage,
    generate_image,
    generate_slide_visual,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/visual", tags=["Visual Synthesis"])


class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""
    prompt: str = Field(description="Description of the image to generate")
    style_prompt: Optional[str] = Field(default="", description="Additional style keywords")
    size: str = Field(default="1024x1024", description="Image size: 256x256, 512x512, 1024x1024, etc.")
    style: str = Field(default="natural", description="Style: vivid, natural, photorealistic, illustration")


class SlideVisualRequest(BaseModel):
    """Request for generating a slide visual."""
    visual_prompt: str = Field(description="What the visual should depict")
    style_gene_prompt: Optional[str] = Field(default="", description="Style prompt from the presentation theme")
    visual_type: str = Field(default="image", description="Type: image, icon, background")


class ImageResponse(BaseModel):
    """Response with generated image."""
    success: bool
    filename: str
    prompt_used: str
    model_used: str
    generation_time_ms: int
    image_base64: Optional[str] = None
    saved_path: Optional[str] = None


@router.post("/generate", response_model=ImageResponse)
async def generate_image_endpoint(request: ImageGenerationRequest):
    """
    Generate an image from a text prompt.
    
    Uses the best available AI backend (OpenAI DALL-E, Stability AI, or Placeholder).
    Returns the generated image as base64.
    """
    try:
        # Map size string to enum
        size_map = {
            "256x256": ImageSize.SMALL,
            "512x512": ImageSize.MEDIUM,
            "1024x1024": ImageSize.LARGE,
            "1792x1024": ImageSize.WIDE,
            "1024x1792": ImageSize.TALL,
        }
        size = size_map.get(request.size, ImageSize.LARGE)
        
        # Map style string to enum
        style_map = {
            "vivid": ImageStyle.VIVID,
            "natural": ImageStyle.NATURAL,
            "photorealistic": ImageStyle.PHOTOREALISTIC,
            "illustration": ImageStyle.ILLUSTRATION,
            "corporate": ImageStyle.CORPORATE,
            "minimal": ImageStyle.MINIMAL,
        }
        style = style_map.get(request.style.lower(), ImageStyle.NATURAL)
        
        generator = ImageGenerator()
        image = await generator.generate(
            prompt=request.prompt,
            style_prompt=request.style_prompt,
            size=size,
            style=style,
            save_to_disk=True,
        )
        
        # Convert to base64 for response
        image_b64 = base64.b64encode(image.image_data).decode("utf-8")
        
        return ImageResponse(
            success=True,
            filename=image.filename,
            prompt_used=image.prompt_used,
            model_used=image.model_used,
            generation_time_ms=image.generation_time_ms,
            image_base64=image_b64,
            saved_path=image.metadata.get("saved_path"),
        )
        
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {str(e)}"
        )


@router.post("/slide-visual", response_model=ImageResponse)
async def generate_slide_visual_endpoint(request: SlideVisualRequest):
    """
    Generate a visual specifically for a presentation slide.
    
    Optimized for slide content with appropriate sizing and styling.
    """
    try:
        generator = ImageGenerator()
        image = await generator.generate_for_slide(
            visual_prompt=request.visual_prompt,
            style_gene_prompt=request.style_gene_prompt or "",
            visual_type=request.visual_type,
        )
        
        image_b64 = base64.b64encode(image.image_data).decode("utf-8")
        
        return ImageResponse(
            success=True,
            filename=image.filename,
            prompt_used=image.prompt_used,
            model_used=image.model_used,
            generation_time_ms=image.generation_time_ms,
            image_base64=image_b64,
            saved_path=image.metadata.get("saved_path"),
        )
        
    except Exception as e:
        logger.error(f"Slide visual generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Slide visual generation failed: {str(e)}"
        )


@router.get("/backends")
async def list_available_backends():
    """
    List available image generation backends.
    
    Returns which AI services are configured and ready to use.
    """
    generator = ImageGenerator()
    available = generator.get_available_backends()
    
    return {
        "available_backends": available,
        "preferred": generator.preferred_backend,
        "has_ai_backend": "openai" in available or "stability" in available,
    }


@router.get("/health")
async def health_check():
    """Check if Visual Synthesis service is operational."""
    generator = ImageGenerator()
    available = generator.get_available_backends()
    
    return {
        "status": "healthy",
        "service": "visual_synthesis",
        "backends_available": len(available),
        "has_ai_backend": "openai" in available or "stability" in available,
    }
