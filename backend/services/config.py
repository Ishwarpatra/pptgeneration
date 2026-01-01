"""
Centralized configuration for the PPT Generation service.
Contains slide dimensions, default values, and other configurable parameters.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Tuple
import os


class AspectRatio(str, Enum):
    """Supported slide aspect ratios."""
    WIDESCREEN_16_9 = "16:9"
    STANDARD_4_3 = "4:3"
    WIDESCREEN_16_10 = "16:10"
    ULTRAWIDE_21_9 = "21:9"


@dataclass(frozen=True)
class SlideDimensions:
    """Slide dimension configuration in inches."""
    width: float
    height: float
    aspect_ratio: AspectRatio
    
    @property
    def as_inches_tuple(self) -> Tuple[float, float]:
        """Return (width, height) tuple."""
        return (self.width, self.height)


# Predefined slide dimension presets
SLIDE_DIMENSIONS = {
    AspectRatio.WIDESCREEN_16_9: SlideDimensions(
        width=13.333,
        height=7.5,
        aspect_ratio=AspectRatio.WIDESCREEN_16_9
    ),
    AspectRatio.STANDARD_4_3: SlideDimensions(
        width=10.0,
        height=7.5,
        aspect_ratio=AspectRatio.STANDARD_4_3
    ),
    AspectRatio.WIDESCREEN_16_10: SlideDimensions(
        width=10.0,
        height=6.25,
        aspect_ratio=AspectRatio.WIDESCREEN_16_10
    ),
    AspectRatio.ULTRAWIDE_21_9: SlideDimensions(
        width=14.0,
        height=6.0,
        aspect_ratio=AspectRatio.ULTRAWIDE_21_9
    ),
}


# Default slide dimensions
DEFAULT_ASPECT_RATIO = AspectRatio.WIDESCREEN_16_9
DEFAULT_SLIDE_DIMENSIONS = SLIDE_DIMENSIONS[DEFAULT_ASPECT_RATIO]


def get_slide_dimensions(aspect_ratio: AspectRatio = None) -> SlideDimensions:
    """
    Get slide dimensions for a given aspect ratio.
    
    Args:
        aspect_ratio: The desired aspect ratio. Defaults to 16:9 widescreen.
        
    Returns:
        SlideDimensions configuration object.
    """
    if aspect_ratio is None:
        aspect_ratio = DEFAULT_ASPECT_RATIO
    return SLIDE_DIMENSIONS.get(aspect_ratio, DEFAULT_SLIDE_DIMENSIONS)


@dataclass
class ServiceConfig:
    """Main service configuration."""
    # Database connections
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/pptgen_db")
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API Keys
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    stability_api_key: str = os.getenv("STABILITY_API_KEY", "")
    
    # File paths
    output_dir: str = os.getenv("OUTPUT_DIR", "presentations")
    images_dir: str = os.getenv("IMAGES_DIR", "generated_images")
    
    # Limits
    max_slides_per_presentation: int = 50
    max_file_upload_mb: int = 50
    image_generation_timeout_seconds: int = 120


# Global configuration instance
config = ServiceConfig()
