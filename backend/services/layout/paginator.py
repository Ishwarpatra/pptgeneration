"""
Layout Engine - Pagination and Block-to-Slide Mapping.
Implements greedy bin packing with context-aware rules.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum

from services.nlp.models import SlideContent, LayoutType, VisualSpec, VisualType


class BlockType(str, Enum):
    """Types of content blocks."""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    BULLET_LIST = "bullet_list"
    NUMBERED_LIST = "numbered_list"
    IMAGE = "image"
    CHART = "chart"
    QUOTE = "quote"
    SPACER = "spacer"


@dataclass
class ContentBlock:
    """A single content block with estimated height."""
    block_type: BlockType
    content: str
    estimated_height_pt: float = 0.0
    level: int = 0  # For nested lists
    visual_spec: Optional[VisualSpec] = None
    keep_with_next: bool = False  # For orphan prevention


# Height constants (in points, standard PowerPoint units)
SLIDE_HEIGHT_PT = 540  # 7.5 inches at 72 DPI
SLIDE_WIDTH_PT = 720   # 10 inches at 72 DPI
TITLE_AREA_PT = 80
FOOTER_AREA_PT = 30
CONTENT_AREA_PT = SLIDE_HEIGHT_PT - TITLE_AREA_PT - FOOTER_AREA_PT

# Block height estimates
BLOCK_HEIGHTS = {
    BlockType.HEADING: 60,
    BlockType.PARAGRAPH: 45,
    BlockType.BULLET_LIST: 25,  # Per item
    BlockType.NUMBERED_LIST: 28,
    BlockType.IMAGE: 200,
    BlockType.CHART: 250,
    BlockType.QUOTE: 60,
    BlockType.SPACER: 20,
}


@dataclass
class SlideSpec:
    """Specification for a compiled slide."""
    title: str
    layout_type: LayoutType
    blocks: List[ContentBlock] = field(default_factory=list)
    visual_spec: Optional[VisualSpec] = None
    speaker_notes: str = ""
    total_height_pt: float = 0.0
    is_continuation: bool = False
    continuation_marker: str = ""


class Paginator:
    """
    Greedy bin packing paginator.
    Maps flowing content blocks to discrete slides.
    """

    def __init__(
        self,
        max_content_height: float = CONTENT_AREA_PT,
        title_height: float = TITLE_AREA_PT
    ):
        self.max_content_height = max_content_height
        self.title_height = title_height

    def _estimate_block_height(self, block: ContentBlock) -> float:
        """Estimate the height of a content block."""
        if block.estimated_height_pt > 0:
            return block.estimated_height_pt
        
        base_height = BLOCK_HEIGHTS.get(block.block_type, 30)
        
        # Adjust for content length
        if block.block_type == BlockType.PARAGRAPH:
            # Rough estimate: 60 chars per line, 20pt per line
            lines = len(block.content) / 60
            base_height = max(base_height, lines * 20)
        elif block.block_type in (BlockType.BULLET_LIST, BlockType.NUMBERED_LIST):
            # Already per-item height
            pass
        
        return base_height

    def _should_keep_together(
        self,
        current_block: ContentBlock,
        next_block: Optional[ContentBlock]
    ) -> bool:
        """Check if current block should stay with next block."""
        if current_block.keep_with_next:
            return True
        
        # Headings should not be orphaned at end of slide
        if current_block.block_type == BlockType.HEADING:
            return True
        
        return False

    def _can_fit_on_slide(
        self,
        current_slide: SlideSpec,
        block: ContentBlock
    ) -> bool:
        """Check if a block can fit on the current slide."""
        block_height = self._estimate_block_height(block)
        return (current_slide.total_height_pt + block_height) <= self.max_content_height

    def paginate_slide_content(
        self,
        slide: SlideContent
    ) -> List[SlideSpec]:
        """
        Take a SlideContent and paginate it if needed.
        Most slides won't need pagination, but this handles overflow.
        """
        # Convert body text to blocks
        blocks = []
        for text in slide.body_text:
            blocks.append(ContentBlock(
                block_type=BlockType.BULLET_LIST,
                content=text,
                estimated_height_pt=BLOCK_HEIGHTS[BlockType.BULLET_LIST],
            ))
        
        # Simple case: everything fits
        total_height = sum(self._estimate_block_height(b) for b in blocks)
        if total_height <= self.max_content_height:
            return [SlideSpec(
                title=slide.title,
                layout_type=slide.layout_type,
                blocks=blocks,
                visual_spec=slide.visual_spec,
                speaker_notes=slide.speaker_notes,
                total_height_pt=total_height,
            )]
        
        # Need to split across slides
        slides = []
        current_slide = SlideSpec(
            title=slide.title,
            layout_type=slide.layout_type,
            visual_spec=slide.visual_spec if not slides else None,
            speaker_notes=slide.speaker_notes if not slides else "",
        )
        
        for i, block in enumerate(blocks):
            next_block = blocks[i + 1] if i + 1 < len(blocks) else None
            
            if self._can_fit_on_slide(current_slide, block):
                current_slide.blocks.append(block)
                current_slide.total_height_pt += self._estimate_block_height(block)
            else:
                # Start new slide
                if current_slide.blocks:
                    slides.append(current_slide)
                
                current_slide = SlideSpec(
                    title=slide.title,
                    layout_type=slide.layout_type,
                    is_continuation=True,
                    continuation_marker="(Continued)",
                )
                current_slide.blocks.append(block)
                current_slide.total_height_pt = self._estimate_block_height(block)
        
        # Don't forget the last slide
        if current_slide.blocks:
            slides.append(current_slide)
        
        return slides

    def paginate_presentation(
        self,
        slides: List[SlideContent]
    ) -> List[SlideSpec]:
        """
        Paginate an entire presentation.
        """
        result = []
        for slide in slides:
            paginated = self.paginate_slide_content(slide)
            result.extend(paginated)
        return result


class LayoutOptimizer:
    """
    Optimizes layout decisions for slides.
    Determines best layout type based on content.
    """

    @staticmethod
    def suggest_layout(slide: SlideContent) -> LayoutType:
        """Suggest optimal layout based on content analysis."""
        has_visual = (
            slide.visual_spec and 
            slide.visual_spec.visual_type != VisualType.NONE
        )
        text_count = len(slide.body_text)
        
        # Title-only slides
        if text_count == 0 and not has_visual:
            return LayoutType.TITLE_ONLY
        
        # Section headers
        if text_count <= 1 and not has_visual:
            return LayoutType.SECTION_HEADER
        
        # Visual-heavy slides
        if has_visual:
            if text_count <= 2:
                return LayoutType.VISUAL_HEAVY
            else:
                return LayoutType.TWO_COLUMN
        
        # Comparison slides (detected by content patterns)
        if text_count >= 4 and text_count % 2 == 0:
            # Could be a comparison/two-column situation
            return LayoutType.TWO_COLUMN
        
        # Default content layout
        return LayoutType.TITLE_CONTENT

    @staticmethod
    def calculate_density_score(slide: SlideSpec) -> float:
        """
        Calculate content density score (0.0 = empty, 1.0 = packed).
        Used for visual balance analysis.
        """
        return slide.total_height_pt / CONTENT_AREA_PT
