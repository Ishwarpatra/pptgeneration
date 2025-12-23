"""
API Routes for Style Engine.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from .presets import (
    list_presets,
    get_preset,
    breed_styles,
    STYLE_PRESETS,
)
from .style_gene import StyleGene

router = APIRouter(prefix="/api/style", tags=["Style Engine"])


class StylePreviewResponse(BaseModel):
    """Response model for style preview."""
    id: str
    name: str
    tags: List[str]
    preview_colors: dict
    css_variables: Optional[dict] = None


class BreedRequest(BaseModel):
    """Request model for breeding styles."""
    parent_a: str = Field(description="ID of first parent style")
    parent_b: str = Field(description="ID of second parent style")
    alpha: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Mixing factor: 0.0 = 100% parent_a, 1.0 = 100% parent_b"
    )


class BreedResponse(BaseModel):
    """Response model for bred style."""
    gene_id: str
    name: str
    css_variables: dict
    visual_prompt: str
    palette: dict


@router.get("/presets", response_model=List[StylePreviewResponse])
async def get_all_presets():
    """
    List all available style presets.
    Returns preview information for each preset.
    """
    presets = list_presets()
    return [
        StylePreviewResponse(
            id=p["id"],
            name=p["name"],
            tags=p["tags"],
            preview_colors=p["preview_colors"],
        )
        for p in presets
    ]


@router.get("/presets/{preset_id}")
async def get_preset_details(preset_id: str):
    """
    Get full details of a specific preset including CSS variables.
    """
    try:
        preset = get_preset(preset_id)
        return {
            "id": preset.gene_id,
            "name": preset.name,
            "tags": preset.tags,
            "css_variables": preset.to_css_variables(),
            "visual_prompt": preset.visual_style_prompt,
            "palette": preset.palette.to_hex_dict(),
            "typography": {
                "heading_font": preset.typography.heading_font,
                "body_font": preset.typography.body_font,
                "sizes": preset.typography.get_heading_sizes(),
            },
            "layout": {
                "density": preset.layout.density,
                "corner_radius": preset.layout.corner_radius,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/breed", response_model=BreedResponse)
async def breed_styles_endpoint(request: BreedRequest):
    """
    Breed two styles together Artbreeder-style.
    
    Creates a new child style by interpolating between two parent styles.
    The alpha parameter controls the mixing ratio.
    """
    try:
        child = breed_styles(
            request.parent_a,
            request.parent_b,
            request.alpha
        )
        return BreedResponse(
            gene_id=child.gene_id,
            name=child.name,
            css_variables=child.to_css_variables(),
            visual_prompt=child.visual_style_prompt,
            palette=child.palette.to_hex_dict(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/interpolate")
async def interpolate_preview(
    parent_a: str = Query(..., description="First parent preset ID"),
    parent_b: str = Query(..., description="Second parent preset ID"),
    steps: int = Query(default=5, ge=2, le=11, description="Number of interpolation steps")
):
    """
    Generate a series of interpolated styles between two parents.
    Useful for previewing the breeding gradient.
    """
    try:
        results = []
        for i in range(steps):
            alpha = i / (steps - 1)
            child = breed_styles(parent_a, parent_b, alpha)
            results.append({
                "alpha": alpha,
                "palette": child.palette.to_hex_dict(),
                "css_variables": child.to_css_variables(),
            })
        return {
            "parent_a": parent_a,
            "parent_b": parent_b,
            "steps": results,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def health_check():
    """Check if Style Engine is operational."""
    return {
        "status": "healthy",
        "service": "style_engine",
        "presets_count": len(STYLE_PRESETS),
    }
