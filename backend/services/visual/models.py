# Visual Synthesis Types
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class ImageStyle(str, Enum):
    """AI Image generation styles"""
    PHOTOREALISTIC = "photorealistic"
    ILLUSTRATION = "illustration"
    FLAT_DESIGN = "flat_design"
    ISOMETRIC = "isometric"
    WATERCOLOR = "watercolor"
    MINIMALIST = "minimalist"
    CORPORATE = "corporate"
    ABSTRACT = "abstract"
    INFOGRAPHIC = "infographic"
    ICON = "icon"


class AspectRatio(str, Enum):
    """Common aspect ratios for presentations"""
    WIDESCREEN = "16:9"  # Standard presentation
    STANDARD = "4:3"     # Legacy presentations
    SQUARE = "1:1"       # Social media
    PORTRAIT = "9:16"    # Mobile


class ImageGenerationRequest(BaseModel):
    """Request for AI image generation"""
    prompt: str = Field(..., description="Description of the image to generate")
    style: ImageStyle = Field(default=ImageStyle.CORPORATE, description="Visual style")
    aspect_ratio: AspectRatio = Field(default=AspectRatio.WIDESCREEN, description="Image aspect ratio")
    negative_prompt: Optional[str] = Field(default=None, description="What to avoid in the image")
    color_palette: Optional[List[str]] = Field(default=None, description="Colors to incorporate")
    slide_context: Optional[str] = Field(default=None, description="Context from slide content")
    quality: Literal["draft", "standard", "high"] = Field(default="standard")


class ImageGenerationResponse(BaseModel):
    """Response from image generation"""
    success: bool
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    prompt_used: str
    style: ImageStyle
    error: Optional[str] = None
    credits_used: int = 1


class ImageSuggestion(BaseModel):
    """AI-suggested image for slide content"""
    suggested_prompt: str
    confidence: float
    style: ImageStyle
    rationale: str


class SlideImageAnalysis(BaseModel):
    """Analysis of what images would suit a slide"""
    slide_title: str
    slide_content: str
    suggestions: List[ImageSuggestion]
    recommended_count: int
