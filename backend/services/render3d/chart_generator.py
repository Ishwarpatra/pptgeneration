"""
3D Chart Generator - Creates 3D charts and visualizations.
Supports basic 3D charts with fallback to 2D for environments without Blender.
"""
import io
import math
from pathlib import Path
from typing import List, Dict, Optional, Literal, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class ChartType(str, Enum):
    """Supported chart types."""
    BAR = "bar"
    PIE = "pie"
    LINE = "line"
    DONUT = "donut"
    COLUMN = "column"


class ChartStyle(str, Enum):
    """Visual style for charts."""
    FLAT = "flat"
    ISOMETRIC = "isometric"
    GLASS = "glass"
    SOLID = "solid"


@dataclass
class ChartData:
    """Data for chart generation."""
    labels: List[str]
    values: List[float]
    title: str = ""
    colors: Optional[List[str]] = None


@dataclass
class ChartConfig:
    """Configuration for chart rendering."""
    chart_type: ChartType = ChartType.BAR
    style: ChartStyle = ChartStyle.ISOMETRIC
    width: int = 800
    height: int = 600
    background_color: str = "#ffffff"
    primary_color: str = "#3b82f6"
    secondary_colors: Optional[List[str]] = None
    show_legend: bool = True
    show_values: bool = True
    shadow: bool = True


@dataclass
class RenderedChart:
    """Result of chart rendering."""
    image_data: bytes
    filename: str
    chart_type: str
    render_time_ms: int


class IsometricChartRenderer:
    """
    Renders isometric-style 3D charts using PIL.
    Provides a Blender-like aesthetic without requiring Blender.
    """

    def __init__(self, config: ChartConfig):
        self.config = config
        self.default_colors = [
            "#3b82f6",  # Blue
            "#10b981",  # Green
            "#f59e0b",  # Amber
            "#ef4444",  # Red
            "#8b5cf6",  # Purple
            "#06b6d4",  # Cyan
            "#ec4899",  # Pink
            "#f97316",  # Orange
        ]

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _darken_color(self, color: Tuple[int, int, int], factor: float = 0.7) -> Tuple[int, int, int]:
        """Darken a color by a factor."""
        return tuple(int(c * factor) for c in color)

    def _lighten_color(self, color: Tuple[int, int, int], factor: float = 1.3) -> Tuple[int, int, int]:
        """Lighten a color by a factor."""
        return tuple(min(255, int(c * factor)) for c in color)

    def _get_colors(self, count: int) -> List[str]:
        """Get a list of colors for the chart."""
        if self.config.secondary_colors:
            return self.config.secondary_colors[:count]
        return self.default_colors[:count]

    def _draw_isometric_bar(
        self,
        draw: ImageDraw.Draw,
        x: int,
        y: int,
        width: int,
        height: int,
        depth: int,
        color: str
    ):
        """Draw an isometric 3D bar."""
        rgb = self._hex_to_rgb(color)
        dark = self._darken_color(rgb, 0.6)
        medium = self._darken_color(rgb, 0.8)
        
        # Front face
        front = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
        ]
        draw.polygon(front, fill=rgb)
        
        # Top face (isometric)
        top = [
            (x, y),
            (x + depth, y - depth//2),
            (x + width + depth, y - depth//2),
            (x + width, y),
        ]
        draw.polygon(top, fill=self._lighten_color(rgb))
        
        # Right face
        right = [
            (x + width, y),
            (x + width + depth, y - depth//2),
            (x + width + depth, y + height - depth//2),
            (x + width, y + height),
        ]
        draw.polygon(right, fill=medium)

    def render_bar_chart(self, data: ChartData) -> Image.Image:
        """Render an isometric bar chart."""
        img = Image.new("RGBA", (self.config.width, self.config.height), 
                       self._hex_to_rgb(self.config.background_color) + (255,))
        draw = ImageDraw.Draw(img)
        
        # Calculate dimensions
        num_bars = len(data.values)
        max_value = max(data.values) if data.values else 1
        
        margin = 80
        chart_width = self.config.width - margin * 2
        chart_height = self.config.height - margin * 2 - 50
        
        bar_width = min(60, chart_width // (num_bars * 2))
        bar_spacing = chart_width // num_bars
        bar_depth = 20
        
        colors = self._get_colors(num_bars)
        
        # Draw bars
        base_y = self.config.height - margin
        
        for i, (value, label) in enumerate(zip(data.values, data.labels)):
            bar_height = int((value / max_value) * chart_height)
            x = margin + i * bar_spacing + bar_spacing // 4
            y = base_y - bar_height
            
            self._draw_isometric_bar(
                draw, x, y, bar_width, bar_height, bar_depth,
                colors[i % len(colors)]
            )
            
            # Draw label
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            # Label below bar
            label_text = label[:10] + "..." if len(label) > 10 else label
            draw.text((x + bar_width // 2, base_y + 10), label_text, 
                     fill=(80, 80, 80), font=font, anchor="mt")
            
            # Value on top
            if self.config.show_values:
                value_text = f"{value:.0f}" if value == int(value) else f"{value:.1f}"
                draw.text((x + bar_width // 2, y - 15), value_text,
                         fill=(60, 60, 60), font=font, anchor="mb")
        
        # Draw title
        if data.title:
            try:
                title_font = ImageFont.truetype("arial.ttf", 18)
            except:
                title_font = ImageFont.load_default()
            draw.text((self.config.width // 2, 25), data.title,
                     fill=(40, 40, 40), font=title_font, anchor="mt")
        
        return img

    def render_pie_chart(self, data: ChartData) -> Image.Image:
        """Render a 3D pie chart."""
        img = Image.new("RGBA", (self.config.width, self.config.height),
                       self._hex_to_rgb(self.config.background_color) + (255,))
        draw = ImageDraw.Draw(img)
        
        total = sum(data.values)
        if total == 0:
            return img
        
        colors = self._get_colors(len(data.values))
        
        # Pie dimensions
        center_x = self.config.width // 2
        center_y = self.config.height // 2
        radius = min(self.config.width, self.config.height) // 3
        depth = 30
        
        # Draw 3D effect (bottom slices)
        for d in range(depth, 0, -2):
            start_angle = 0
            for i, value in enumerate(data.values):
                sweep = (value / total) * 360
                color = self._darken_color(self._hex_to_rgb(colors[i % len(colors)]), 0.5)
                
                bbox = [
                    center_x - radius,
                    center_y - radius // 2 + d,
                    center_x + radius,
                    center_y + radius // 2 + d,
                ]
                draw.pieslice(bbox, start_angle, start_angle + sweep, fill=color)
                start_angle += sweep
        
        # Draw top pie
        start_angle = 0
        for i, value in enumerate(data.values):
            sweep = (value / total) * 360
            color = self._hex_to_rgb(colors[i % len(colors)])
            
            bbox = [
                center_x - radius,
                center_y - radius // 2,
                center_x + radius,
                center_y + radius // 2,
            ]
            draw.pieslice(bbox, start_angle, start_angle + sweep, fill=color)
            start_angle += sweep
        
        # Draw legend
        if self.config.show_legend:
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            legend_y = 50
            for i, (label, value) in enumerate(zip(data.labels, data.values)):
                color = self._hex_to_rgb(colors[i % len(colors)])
                
                # Color box
                draw.rectangle([20, legend_y, 35, legend_y + 15], fill=color)
                
                # Label
                percent = (value / total) * 100
                text = f"{label}: {percent:.1f}%"
                draw.text((45, legend_y), text, fill=(60, 60, 60), font=font)
                
                legend_y += 25
        
        # Draw title
        if data.title:
            try:
                title_font = ImageFont.truetype("arial.ttf", 18)
            except:
                title_font = ImageFont.load_default()
            draw.text((self.config.width // 2, 20), data.title,
                     fill=(40, 40, 40), font=title_font, anchor="mt")
        
        return img

    def render_line_chart(self, data: ChartData) -> Image.Image:
        """Render a line chart with 3D styling."""
        img = Image.new("RGBA", (self.config.width, self.config.height),
                       self._hex_to_rgb(self.config.background_color) + (255,))
        draw = ImageDraw.Draw(img)
        
        if not data.values:
            return img
        
        max_value = max(data.values)
        min_value = min(data.values)
        value_range = max_value - min_value if max_value != min_value else 1
        
        margin = 80
        chart_width = self.config.width - margin * 2
        chart_height = self.config.height - margin * 2
        
        num_points = len(data.values)
        point_spacing = chart_width // max(1, num_points - 1)
        
        # Calculate points
        points = []
        for i, value in enumerate(data.values):
            x = margin + i * point_spacing
            y = self.config.height - margin - int(((value - min_value) / value_range) * chart_height)
            points.append((x, y))
        
        # Draw grid
        for i in range(5):
            y = margin + i * (chart_height // 4)
            draw.line([(margin, y), (self.config.width - margin, y)], 
                     fill=(220, 220, 220), width=1)
        
        # Draw line with shadow
        color = self._hex_to_rgb(self.config.primary_color)
        
        if len(points) > 1:
            # Shadow
            shadow_points = [(p[0] + 3, p[1] + 3) for p in points]
            draw.line(shadow_points, fill=(200, 200, 200), width=4)
            
            # Main line
            draw.line(points, fill=color, width=3)
        
        # Draw points
        for i, (x, y) in enumerate(points):
            draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=color, outline=(255, 255, 255))
            
            # Value label
            if self.config.show_values:
                try:
                    font = ImageFont.truetype("arial.ttf", 10)
                except:
                    font = ImageFont.load_default()
                value_text = f"{data.values[i]:.0f}"
                draw.text((x, y - 15), value_text, fill=(60, 60, 60), font=font, anchor="mb")
        
        # Draw labels
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        for i, (x, _) in enumerate(points):
            if i < len(data.labels):
                label = data.labels[i][:8]
                draw.text((x, self.config.height - margin + 15), label,
                         fill=(80, 80, 80), font=font, anchor="mt")
        
        # Title
        if data.title:
            try:
                title_font = ImageFont.truetype("arial.ttf", 18)
            except:
                title_font = ImageFont.load_default()
            draw.text((self.config.width // 2, 25), data.title,
                     fill=(40, 40, 40), font=title_font, anchor="mt")
        
        return img

    def render(self, data: ChartData) -> RenderedChart:
        """Render a chart based on configuration."""
        start_time = datetime.now()
        
        if self.config.chart_type == ChartType.BAR or self.config.chart_type == ChartType.COLUMN:
            img = self.render_bar_chart(data)
        elif self.config.chart_type == ChartType.PIE or self.config.chart_type == ChartType.DONUT:
            img = self.render_pie_chart(data)
        elif self.config.chart_type == ChartType.LINE:
            img = self.render_line_chart(data)
        else:
            img = self.render_bar_chart(data)  # Default
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        
        end_time = datetime.now()
        render_time = int((end_time - start_time).total_seconds() * 1000)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return RenderedChart(
            image_data=image_bytes,
            filename=f"chart_{self.config.chart_type.value}_{timestamp}.png",
            chart_type=self.config.chart_type.value,
            render_time_ms=render_time,
        )


class ChartGenerator:
    """
    Main chart generation service.
    Uses isometric rendering for 3D-style charts.
    """

    def __init__(self):
        self.output_dir = Path("generated_charts")
        self.output_dir.mkdir(exist_ok=True)

    def generate(
        self,
        data: ChartData,
        chart_type: ChartType = ChartType.BAR,
        style: ChartStyle = ChartStyle.ISOMETRIC,
        colors: Optional[List[str]] = None,
        save_to_disk: bool = True,
    ) -> RenderedChart:
        """
        Generate a 3D-style chart.
        
        Args:
            data: Chart data with labels and values
            chart_type: Type of chart to render
            style: Visual style
            colors: Optional list of colors to use
            save_to_disk: Whether to save the file
            
        Returns:
            RenderedChart with the image data
        """
        config = ChartConfig(
            chart_type=chart_type,
            style=style,
            secondary_colors=colors,
        )
        
        renderer = IsometricChartRenderer(config)
        result = renderer.render(data)
        
        if save_to_disk:
            file_path = self.output_dir / result.filename
            with open(file_path, "wb") as f:
                f.write(result.image_data)
        
        return result

    def generate_bar_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str = "",
        colors: Optional[List[str]] = None,
    ) -> RenderedChart:
        """Generate an isometric bar chart."""
        data = ChartData(labels=labels, values=values, title=title)
        return self.generate(data, ChartType.BAR, colors=colors)

    def generate_pie_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str = "",
        colors: Optional[List[str]] = None,
    ) -> RenderedChart:
        """Generate a 3D pie chart."""
        data = ChartData(labels=labels, values=values, title=title)
        return self.generate(data, ChartType.PIE, colors=colors)

    def generate_line_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str = "",
    ) -> RenderedChart:
        """Generate a styled line chart."""
        data = ChartData(labels=labels, values=values, title=title)
        return self.generate(data, ChartType.LINE)


# Convenience functions
def render_bar_chart(labels: List[str], values: List[float], title: str = "") -> RenderedChart:
    """Quick function to render a bar chart."""
    generator = ChartGenerator()
    return generator.generate_bar_chart(labels, values, title)


def render_pie_chart(labels: List[str], values: List[float], title: str = "") -> RenderedChart:
    """Quick function to render a pie chart."""
    generator = ChartGenerator()
    return generator.generate_pie_chart(labels, values, title)
