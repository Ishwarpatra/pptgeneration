# Visual Synthesis API Routes
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional
from .models import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageStyle,
    SlideImageAnalysis,
    AspectRatio
)
from .engine import get_visual_engine

router = APIRouter(prefix="/api/visual", tags=["Visual Synthesis"])


@router.get("/styles")
async def list_image_styles():
    """
    List all available image generation styles
    """
    return {
        "styles": [
            {
                "id": style.value,
                "name": style.name.replace("_", " ").title(),
                "description": _get_style_description(style)
            }
            for style in ImageStyle
        ]
    }


@router.get("/aspect-ratios")
async def list_aspect_ratios():
    """
    List available aspect ratios for image generation
    """
    return {
        "aspect_ratios": [
            {
                "id": ratio.value,
                "name": ratio.name.replace("_", " ").title(),
                "recommended_for": _get_ratio_use_case(ratio)
            }
            for ratio in AspectRatio
        ]
    }


@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """
    Generate an AI image based on the provided prompt and style.
    
    Supports multiple providers:
    - Google Gemini (Imagen) (if GEMINI_API_KEY is set)
    - Stability AI (if STABILITY_API_KEY is set)
    - Placeholder (fallback for development)
    """
    engine = get_visual_engine()
    result = await engine.generate_image(request)
    
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    
    return result


@router.post("/suggest")
async def suggest_images_for_slide(
    slide_title: str,
    slide_content: str,
    style_preference: Optional[ImageStyle] = None
) -> SlideImageAnalysis:
    """
    Analyze slide content and suggest appropriate images.
    
    Uses AI to understand the context and recommend relevant visuals.
    """
    engine = get_visual_engine()
    return await engine.suggest_images_for_slide(
        slide_title=slide_title,
        slide_content=slide_content,
        style_preference=style_preference
    )


@router.get("/image/{filename}")
async def get_generated_image(filename: str):
    """
    Retrieve a previously generated image by filename.
    """
    image_path = Path("generated_images") / filename
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Determine media type
    suffix = image_path.suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
        ".webp": "image/webp"
    }
    media_type = media_types.get(suffix, "application/octet-stream")
    
    return FileResponse(image_path, media_type=media_type)


@router.get("/provider")
async def get_current_provider():
    """
    Get information about the current image generation provider.
    """
    engine = get_visual_engine()
    
    provider_info = {
        "gemini": {
            "name": "Google Gemini (Imagen)",
            "quality": "High",
            "speed": "Fast",
            "cost": "Pay per image"
        },
        "stability": {
            "name": "Stability AI",
            "quality": "High",
            "speed": "Medium",
            "cost": "Pay per image"
        },
        "placeholder": {
            "name": "Placeholder (Development)",
            "quality": "N/A",
            "speed": "Instant",
            "cost": "Free"
        }
    }
    
    return {
        "current_provider": engine.provider,
        "details": provider_info.get(engine.provider, {}),
        "available_styles": len(ImageStyle),
        "available_ratios": len(AspectRatio)
    }


def _get_style_description(style: ImageStyle) -> str:
    """Get human-readable description for each style"""
    descriptions = {
        ImageStyle.PHOTOREALISTIC: "Realistic photography-like images",
        ImageStyle.ILLUSTRATION: "Digital art and illustrations",
        ImageStyle.FLAT_DESIGN: "Modern flat UI design style",
        ImageStyle.ISOMETRIC: "3D isometric perspective views",
        ImageStyle.WATERCOLOR: "Artistic watercolor painting style",
        ImageStyle.MINIMALIST: "Simple, clean, minimal designs",
        ImageStyle.CORPORATE: "Professional business imagery",
        ImageStyle.ABSTRACT: "Abstract artistic compositions",
        ImageStyle.INFOGRAPHIC: "Data visualization and infographics",
        ImageStyle.ICON: "Simple icon-style graphics",
    }
    return descriptions.get(style, "")


def _get_ratio_use_case(ratio: AspectRatio) -> str:
    """Get recommended use case for each aspect ratio"""
    use_cases = {
        AspectRatio.WIDESCREEN: "Standard presentations (PowerPoint, Google Slides)",
        AspectRatio.STANDARD: "Legacy presentations and documents",
        AspectRatio.SQUARE: "Social media and thumbnails",
        AspectRatio.PORTRAIT: "Mobile-first and story formats",
    }
    return use_cases.get(ratio, "")
