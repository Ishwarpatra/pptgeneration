"""
PPTX Compiler - Generates PowerPoint files from structured content.
Uses python-pptx to create professional presentations.
"""
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from services.nlp.models import PresentationOutline, SlideContent, LayoutType, VisualType
from services.style.style_gene import StyleGene
from services.style.presets import get_preset, MODERN_MINIMAL
from .paginator import Paginator, SlideSpec


class PPTXCompiler:
    """
    Compiles presentation outlines into PowerPoint files.
    Applies Style Genes to formatting.
    """

    def __init__(
        self,
        style: Optional[StyleGene] = None,
        output_dir: str = "presentations"
    ):
        """
        Initialize the compiler.
        
        Args:
            style: StyleGene to apply (defaults to Modern Minimal)
            output_dir: Directory to save generated files
        """
        self.style = style or MODERN_MINIMAL
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.paginator = Paginator()

    def _hex_to_rgb(self, hex_color: str) -> RGBColor:
        """Convert hex color to RGBColor."""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return RGBColor(r, g, b)

    def _apply_style_to_text(self, text_frame, is_title: bool = False):
        """Apply style gene formatting to a text frame."""
        colors = self.style.palette.to_hex_dict()
        typo = self.style.typography
        sizes = typo.get_heading_sizes()
        
        for paragraph in text_frame.paragraphs:
            for run in paragraph.runs:
                # Font family
                run.font.name = typo.heading_font if is_title else typo.body_font
                
                # Font size
                if is_title:
                    run.font.size = Pt(sizes["h1"])
                else:
                    run.font.size = Pt(sizes["body"])
                
                # Color
                run.font.color.rgb = self._hex_to_rgb(colors["text_primary"])

    def _get_layout_index(self, layout_type: LayoutType, prs: Presentation) -> int:
        """Map LayoutType to PowerPoint layout index."""
        # Standard PowerPoint layout indices:
        # 0 = Title Slide
        # 1 = Title and Content
        # 2 = Section Header
        # 3 = Two Content
        # 4 = Comparison
        # 5 = Title Only
        # 6 = Blank
        
        layout_map = {
            LayoutType.TITLE_ONLY: 5,
            LayoutType.TITLE_CONTENT: 1,
            LayoutType.TWO_COLUMN: 3,
            LayoutType.SECTION_HEADER: 2,
            LayoutType.VISUAL_HEAVY: 1,
            LayoutType.COMPARISON: 4,
            LayoutType.BLANK: 6,
        }
        
        index = layout_map.get(layout_type, 1)
        # Ensure the layout exists
        if index >= len(prs.slide_layouts):
            return 1  # Fallback to Title and Content
        return index

    def _add_title_slide(
        self,
        prs: Presentation,
        title: str,
        subtitle: Optional[str] = None
    ):
        """Add the title slide."""
        layout = prs.slide_layouts[0]  # Title slide layout
        slide = prs.slides.add_slide(layout)
        
        # Set title
        if slide.shapes.title:
            slide.shapes.title.text = title
            self._apply_style_to_text(slide.shapes.title.text_frame, is_title=True)
        
        # Set subtitle
        if subtitle and len(slide.placeholders) > 1:
            subtitle_placeholder = slide.placeholders[1]
            subtitle_placeholder.text = subtitle
            self._apply_style_to_text(subtitle_placeholder.text_frame)

    def _add_content_slide(
        self,
        prs: Presentation,
        slide_content: SlideContent,
        is_continuation: bool = False
    ):
        """Add a content slide."""
        layout_idx = self._get_layout_index(slide_content.layout_type, prs)
        layout = prs.slide_layouts[layout_idx]
        slide = prs.slides.add_slide(layout)
        
        # Set title
        title_text = slide_content.title
        if is_continuation:
            title_text += " (Continued)"
        
        if slide.shapes.title:
            slide.shapes.title.text = title_text
            self._apply_style_to_text(slide.shapes.title.text_frame, is_title=True)
        
        # Find content placeholder
        content_placeholder = None
        for shape in slide.placeholders:
            if shape.placeholder_format.idx == 1:  # Content placeholder
                content_placeholder = shape
                break
        
        if content_placeholder and slide_content.body_text:
            tf = content_placeholder.text_frame
            tf.clear()
            
            for i, point in enumerate(slide_content.body_text):
                if i == 0:
                    tf.paragraphs[0].text = point
                    tf.paragraphs[0].level = 0
                else:
                    p = tf.add_paragraph()
                    p.text = point
                    p.level = 0
            
            self._apply_style_to_text(tf)
        
        # Add speaker notes
        if slide_content.speaker_notes:
            notes_slide = slide.notes_slide
            notes_tf = notes_slide.notes_text_frame
            notes_tf.text = slide_content.speaker_notes

    def _add_visual_placeholder(
        self,
        slide,
        visual_spec
    ):
        """
        Add a placeholder for generated visuals.
        In production, this would embed the actual generated image.
        """
        if not visual_spec or visual_spec.visual_type == VisualType.NONE:
            return
        
        # Add a shape to indicate where the visual goes
        colors = self.style.palette.to_hex_dict()
        
        # Create a placeholder rectangle
        left = Inches(5.5)
        top = Inches(1.5)
        width = Inches(4)
        height = Inches(4)
        
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            left, top, width, height
        )
        
        # Style the placeholder
        shape.fill.solid()
        shape.fill.fore_color.rgb = self._hex_to_rgb(colors["surface"])
        shape.line.color.rgb = self._hex_to_rgb(colors["secondary"])
        
        # Add label
        tf = shape.text_frame
        tf.text = f"[{visual_spec.visual_type.value}]\n{visual_spec.prompt[:50]}..."
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    def compile(
        self,
        outline: PresentationOutline,
        filename: Optional[str] = None
    ) -> str:
        """
        Compile a presentation outline to a PPTX file.
        
        Args:
            outline: The structured presentation outline
            filename: Optional output filename (auto-generated if not provided)
            
        Returns:
            Path to the generated PPTX file
        """
        prs = Presentation()
        
        # Set slide dimensions (widescreen 16:9)
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        
        # Add title slide
        self._add_title_slide(prs, outline.title, outline.subtitle)
        
        # Paginate and add content slides
        paginated_slides = self.paginator.paginate_presentation(outline.slides)
        
        for i, slide_spec in enumerate(outline.slides):
            self._add_content_slide(prs, slide_spec)
            
            # Add visual placeholder if specified
            if slide_spec.visual_spec:
                slide = prs.slides[-1]  # Get the just-added slide
                self._add_visual_placeholder(slide, slide_spec.visual_spec)
        
        # Generate filename
        if not filename:
            safe_title = "".join(c if c.isalnum() else "_" for c in outline.title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_title[:50]}_{timestamp}.pptx"
        
        # Save the file
        output_path = self.output_dir / filename
        prs.save(str(output_path))
        
        return str(output_path)

    def compile_with_style(
        self,
        outline: PresentationOutline,
        style_id: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Compile using a specific style preset.
        """
        self.style = get_preset(style_id)
        return self.compile(outline, filename)


# Convenience function
def generate_pptx(
    outline: PresentationOutline,
    style_id: str = "modern_minimal"
) -> str:
    """
    Quick function to generate a PPTX from an outline.
    
    Args:
        outline: Structured presentation outline
        style_id: Style preset to apply
        
    Returns:
        Path to generated file
    """
    compiler = PPTXCompiler()
    return compiler.compile_with_style(outline, style_id)
