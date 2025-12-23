"""
Pydantic models for structured presentation output.
These models define the schema for LLM-generated slide content.
"""
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from enum import Enum


class LayoutType(str, Enum):
    """Supported slide layout types."""
    TITLE_ONLY = "title_only"
    TITLE_CONTENT = "title_content"
    TWO_COLUMN = "two_column"
    VISUAL_HEAVY = "visual_heavy"
    COMPARISON = "comparison"
    SECTION_HEADER = "section_header"
    BLANK = "blank"


class VisualType(str, Enum):
    """Types of visual elements that can be generated."""
    NONE = "none"
    IMAGE = "image"
    CHART_BAR = "chart_bar"
    CHART_PIE = "chart_pie"
    CHART_LINE = "chart_line"
    ICON_3D = "icon_3d"
    DIAGRAM = "diagram"
    INFOGRAPHIC = "infographic"


class ChartData(BaseModel):
    """Data structure for chart generation."""
    labels: List[str] = Field(description="X-axis labels or category names")
    values: List[float] = Field(description="Numeric values for each label")
    title: Optional[str] = Field(default=None, description="Chart title")


class VisualSpec(BaseModel):
    """Specification for visual element generation."""
    visual_type: VisualType = Field(
        default=VisualType.NONE,
        description="Type of visual to generate"
    )
    prompt: str = Field(
        default="",
        description="Descriptive prompt for image/3D generation"
    )
    chart_data: Optional[ChartData] = Field(
        default=None,
        description="Data for chart generation, if applicable"
    )
    style_keywords: List[str] = Field(
        default_factory=list,
        description="Style keywords: 'minimalist', 'corporate', 'vibrant', etc."
    )


class SlideContent(BaseModel):
    """Complete specification for a single slide."""
    title: str = Field(description="The headline/title of the slide")
    layout_type: LayoutType = Field(
        default=LayoutType.TITLE_CONTENT,
        description="Layout template to use"
    )
    body_text: List[str] = Field(
        default_factory=list,
        description="Bullet points or paragraph text"
    )
    visual_spec: VisualSpec = Field(
        default_factory=VisualSpec,
        description="Specification for visual elements"
    )
    speaker_notes: str = Field(
        default="",
        description="Notes for the presenter (not visible on slide)"
    )
    key_message: str = Field(
        default="",
        description="The single takeaway message for this slide"
    )


class PresentationOutline(BaseModel):
    """Complete presentation structure with all slides."""
    title: str = Field(description="Main presentation title")
    subtitle: Optional[str] = Field(
        default=None,
        description="Optional subtitle or tagline"
    )
    theme_suggestion: str = Field(
        default="professional",
        description="Suggested visual theme: 'corporate', 'creative', 'minimal', etc."
    )
    target_audience: str = Field(
        default="general",
        description="Intended audience for tone calibration"
    )
    slides: List[SlideContent] = Field(
        description="Ordered list of slide specifications"
    )
    estimated_duration_minutes: int = Field(
        default=10,
        description="Estimated presentation duration"
    )


class ContentExpansionRequest(BaseModel):
    """Request model for content expansion API."""
    topic: str = Field(description="Main topic or title for the presentation")
    num_slides: int = Field(
        default=5,
        ge=3,
        le=50,
        description="Number of slides to generate"
    )
    context: Optional[str] = Field(
        default=None,
        description="Additional context or raw content to incorporate"
    )
    style_preference: Optional[str] = Field(
        default=None,
        description="Preferred visual style"
    )
    include_visuals: bool = Field(
        default=True,
        description="Whether to generate visual specifications"
    )
