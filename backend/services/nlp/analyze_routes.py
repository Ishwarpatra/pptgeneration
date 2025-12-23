"""
API Routes for Reference PPT Analysis.
Handles file uploads and style extraction from reference presentations.
"""
import os
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List
import logging

from .reference_analyzer import (
    ReferenceAnalyzer,
    ExtractionResult,
    ExtractedColor,
    ExtractedFont,
    LayoutMetrics,
    analyze_pptx,
    extract_style_from_pptx,
)
from services.style.style_gene import StyleGene

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analyze", tags=["Reference Analysis"])


# Response models
class ColorInfo(BaseModel):
    hex_value: str
    rgb: tuple
    count: int
    context: str = ""


class FontInfo(BaseModel):
    name: str
    count: int
    is_heading: bool
    avg_size_pt: float


class LayoutInfo(BaseModel):
    avg_shapes_per_slide: float
    avg_text_boxes: float
    avg_images: float
    content_density: float
    avg_margin_ratio: float


class AnalysisResponse(BaseModel):
    """Response model for presentation analysis."""
    success: bool
    slide_count: int
    colors: List[ColorInfo]
    fonts: List[FontInfo]
    layout: LayoutInfo
    has_master_theme: bool


class StyleExtractionResponse(BaseModel):
    """Response model for style extraction."""
    success: bool
    gene_id: str
    name: str
    css_variables: dict
    palette: dict
    typography: dict


@router.post("/upload", response_model=AnalysisResponse)
async def analyze_uploaded_pptx(
    file: UploadFile = File(..., description="PowerPoint file to analyze")
):
    """
    Upload and analyze a PowerPoint file.
    
    Extracts colors, fonts, and layout metrics from the presentation.
    Returns detailed analysis that can be used to create a matching style.
    """
    # Validate file type
    if not file.filename.endswith('.pptx'):
        raise HTTPException(
            status_code=400,
            detail="Only .pptx files are supported"
        )
    
    try:
        # Read file contents
        contents = await file.read()
        
        # Analyze the presentation
        analyzer = ReferenceAnalyzer()
        result = analyzer.analyze_from_bytes(contents)
        
        return AnalysisResponse(
            success=True,
            slide_count=result.slide_count,
            colors=[
                ColorInfo(
                    hex_value=c.hex_value,
                    rgb=c.rgb,
                    count=c.count,
                    context=c.context,
                )
                for c in result.colors[:15]  # Top 15 colors
            ],
            fonts=[
                FontInfo(
                    name=f.name,
                    count=f.count,
                    is_heading=f.is_heading,
                    avg_size_pt=f.avg_size_pt,
                )
                for f in result.fonts
            ],
            layout=LayoutInfo(
                avg_shapes_per_slide=result.layout_metrics.avg_shapes_per_slide,
                avg_text_boxes=result.layout_metrics.avg_text_boxes,
                avg_images=result.layout_metrics.avg_images,
                content_density=result.layout_metrics.content_density,
                avg_margin_ratio=result.layout_metrics.avg_margin_ratio,
            ),
            has_master_theme=result.has_master_theme,
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze presentation: {str(e)}"
        )


@router.post("/extract-style", response_model=StyleExtractionResponse)
async def extract_style_from_pptx_upload(
    file: UploadFile = File(..., description="PowerPoint file to extract style from"),
    style_name: str = Form(default="Extracted Style", description="Name for the extracted style")
):
    """
    Extract a Style Gene from an uploaded PowerPoint file.
    
    Analyzes the presentation and creates a Style Gene that can be 
    used to generate new presentations matching the reference style.
    """
    if not file.filename.endswith('.pptx'):
        raise HTTPException(
            status_code=400,
            detail="Only .pptx files are supported"
        )
    
    try:
        contents = await file.read()
        
        analyzer = ReferenceAnalyzer()
        result = analyzer.analyze_from_bytes(contents)
        style_gene = analyzer.extract_style_gene(result, style_name)
        
        return StyleExtractionResponse(
            success=True,
            gene_id=style_gene.gene_id,
            name=style_gene.name,
            css_variables=style_gene.to_css_variables(),
            palette=style_gene.palette.to_hex_dict(),
            typography={
                "heading_font": style_gene.typography.heading_font,
                "body_font": style_gene.typography.body_font,
                "base_size_pt": style_gene.typography.base_size_pt,
                "scale_ratio": style_gene.typography.scale_ratio,
            },
        )
        
    except Exception as e:
        logger.error(f"Style extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract style: {str(e)}"
        )


@router.post("/compare")
async def compare_presentations(
    file1: UploadFile = File(..., description="First PowerPoint file"),
    file2: UploadFile = File(..., description="Second PowerPoint file")
):
    """
    Compare two presentations and show style differences.
    
    Useful for understanding how two presentations differ in their
    visual style and layout approach.
    """
    if not file1.filename.endswith('.pptx') or not file2.filename.endswith('.pptx'):
        raise HTTPException(
            status_code=400,
            detail="Only .pptx files are supported"
        )
    
    try:
        analyzer = ReferenceAnalyzer()
        
        # Analyze both files
        contents1 = await file1.read()
        contents2 = await file2.read()
        
        result1 = analyzer.analyze_from_bytes(contents1)
        result2 = analyzer.analyze_from_bytes(contents2)
        
        style1 = analyzer.extract_style_gene(result1, file1.filename)
        style2 = analyzer.extract_style_gene(result2, file2.filename)
        
        # Calculate similarity scores
        palette1 = style1.palette.to_hex_dict()
        palette2 = style2.palette.to_hex_dict()
        
        matching_colors = sum(
            1 for k in palette1 
            if palette1.get(k) == palette2.get(k)
        )
        color_similarity = matching_colors / len(palette1) if palette1 else 0
        
        font_match = (
            style1.typography.heading_font == style2.typography.heading_font or
            style1.typography.body_font == style2.typography.body_font
        )
        
        density_diff = abs(
            result1.layout_metrics.content_density - 
            result2.layout_metrics.content_density
        )
        
        return {
            "file1": {
                "name": file1.filename,
                "slides": result1.slide_count,
                "primary_color": palette1.get("primary"),
                "heading_font": style1.typography.heading_font,
                "density": result1.layout_metrics.content_density,
            },
            "file2": {
                "name": file2.filename,
                "slides": result2.slide_count,
                "primary_color": palette2.get("primary"),
                "heading_font": style2.typography.heading_font,
                "density": result2.layout_metrics.content_density,
            },
            "comparison": {
                "color_similarity": color_similarity,
                "fonts_match": font_match,
                "density_difference": density_diff,
            }
        }
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check if Analysis service is operational."""
    return {
        "status": "healthy",
        "service": "reference_analysis",
    }
