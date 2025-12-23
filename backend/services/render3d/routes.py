"""
API Routes for 3D Render Service.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import base64
import logging

from .chart_generator import (
    ChartGenerator,
    ChartData,
    ChartType,
    ChartStyle,
    render_bar_chart,
    render_pie_chart,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/render3d", tags=["3D Rendering"])


class ChartDataRequest(BaseModel):
    """Chart data input."""
    labels: List[str] = Field(description="Labels for each data point")
    values: List[float] = Field(description="Numeric values for each label")
    title: str = Field(default="", description="Chart title")


class ChartGenerationRequest(BaseModel):
    """Request for chart generation."""
    data: ChartDataRequest
    chart_type: str = Field(default="bar", description="Type: bar, pie, line, donut")
    style: str = Field(default="isometric", description="Style: isometric, flat, glass")
    colors: Optional[List[str]] = Field(default=None, description="Color hex codes")


class ChartResponse(BaseModel):
    """Response with rendered chart."""
    success: bool
    filename: str
    chart_type: str
    render_time_ms: int
    image_base64: str


@router.post("/chart", response_model=ChartResponse)
async def generate_chart(request: ChartGenerationRequest):
    """
    Generate a 3D-style chart.
    
    Supports bar, pie, line charts with isometric styling.
    Returns the rendered chart as base64 PNG.
    """
    try:
        # Map chart type
        type_map = {
            "bar": ChartType.BAR,
            "pie": ChartType.PIE,
            "line": ChartType.LINE,
            "donut": ChartType.DONUT,
            "column": ChartType.COLUMN,
        }
        chart_type = type_map.get(request.chart_type.lower(), ChartType.BAR)
        
        # Map style
        style_map = {
            "isometric": ChartStyle.ISOMETRIC,
            "flat": ChartStyle.FLAT,
            "glass": ChartStyle.GLASS,
            "solid": ChartStyle.SOLID,
        }
        style = style_map.get(request.style.lower(), ChartStyle.ISOMETRIC)
        
        # Generate chart
        data = ChartData(
            labels=request.data.labels,
            values=request.data.values,
            title=request.data.title,
        )
        
        generator = ChartGenerator()
        result = generator.generate(
            data=data,
            chart_type=chart_type,
            style=style,
            colors=request.colors,
            save_to_disk=True,
        )
        
        # Convert to base64
        image_b64 = base64.b64encode(result.image_data).decode("utf-8")
        
        return ChartResponse(
            success=True,
            filename=result.filename,
            chart_type=result.chart_type,
            render_time_ms=result.render_time_ms,
            image_base64=image_b64,
        )
        
    except Exception as e:
        logger.error(f"Chart generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chart generation failed: {str(e)}"
        )


@router.post("/bar-chart", response_model=ChartResponse)
async def generate_bar_chart(request: ChartDataRequest):
    """
    Quick endpoint for bar chart generation.
    """
    try:
        result = render_bar_chart(
            labels=request.labels,
            values=request.values,
            title=request.title,
        )
        
        image_b64 = base64.b64encode(result.image_data).decode("utf-8")
        
        return ChartResponse(
            success=True,
            filename=result.filename,
            chart_type=result.chart_type,
            render_time_ms=result.render_time_ms,
            image_base64=image_b64,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pie-chart", response_model=ChartResponse)
async def generate_pie_chart(request: ChartDataRequest):
    """
    Quick endpoint for pie chart generation.
    """
    try:
        result = render_pie_chart(
            labels=request.labels,
            values=request.values,
            title=request.title,
        )
        
        image_b64 = base64.b64encode(result.image_data).decode("utf-8")
        
        return ChartResponse(
            success=True,
            filename=result.filename,
            chart_type=result.chart_type,
            render_time_ms=result.render_time_ms,
            image_base64=image_b64,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chart-types")
async def list_chart_types():
    """List available chart types and styles."""
    return {
        "chart_types": ["bar", "pie", "line", "donut", "column"],
        "styles": ["isometric", "flat", "glass", "solid"],
        "default_chart_type": "bar",
        "default_style": "isometric",
    }


@router.get("/health")
async def health_check():
    """Check if 3D Render service is operational."""
    return {
        "status": "healthy",
        "service": "render3d",
        "renderer": "isometric_pil",
    }
