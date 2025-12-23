"""
Visual Synthesis Service - AI Image Generation.
Supports multiple backends: OpenAI DALL-E, Stability AI, and local Stable Diffusion.
"""
import os
import io
import base64
import httpx
import asyncio
from pathlib import Path
from typing import Optional, List, Literal, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import logging

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ImageSize(str, Enum):
    """Standard image sizes for generation."""
    SMALL = "256x256"
    MEDIUM = "512x512"
    LARGE = "1024x1024"
    WIDE = "1792x1024"
    TALL = "1024x1792"


class ImageStyle(str, Enum):
    """Image style presets."""
    VIVID = "vivid"
    NATURAL = "natural"
    PHOTOREALISTIC = "photorealistic"
    ILLUSTRATION = "illustration"
    CORPORATE = "corporate"
    MINIMAL = "minimal"


@dataclass
class GenerationRequest:
    """Request for image generation."""
    prompt: str
    negative_prompt: str = ""
    size: ImageSize = ImageSize.LARGE
    style: ImageStyle = ImageStyle.NATURAL
    style_prompt: str = ""  # Additional style from Style Gene
    num_images: int = 1
    seed: Optional[int] = None


@dataclass
class GeneratedImage:
    """Result of image generation."""
    image_data: bytes
    filename: str
    prompt_used: str
    generation_time_ms: int
    model_used: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ImageGeneratorBackend(ABC):
    """Abstract base class for image generation backends."""
    
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> List[GeneratedImage]:
        """Generate images based on the request."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available."""
        pass


class OpenAIImageGenerator(ImageGeneratorBackend):
    """
    OpenAI DALL-E 3 image generation backend.
    Uses the OpenAI API for high-quality image generation.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/images/generations"
        self.model = "dall-e-3"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def _enhance_prompt(self, request: GenerationRequest) -> str:
        """Enhance the prompt with style information."""
        parts = [request.prompt]
        
        if request.style_prompt:
            parts.append(request.style_prompt)
        
        # Add style-specific enhancements
        style_enhancements = {
            ImageStyle.CORPORATE: "professional, business appropriate, clean design",
            ImageStyle.MINIMAL: "minimalist, simple, clean white background",
            ImageStyle.PHOTOREALISTIC: "photorealistic, high detail, professional photography",
            ImageStyle.ILLUSTRATION: "illustration style, artistic, vector art aesthetic",
        }
        
        if request.style in style_enhancements:
            parts.append(style_enhancements[request.style])
        
        return ", ".join(parts)
    
    async def generate(self, request: GenerationRequest) -> List[GeneratedImage]:
        """Generate images using OpenAI DALL-E 3."""
        if not self.is_available():
            raise RuntimeError("OpenAI API key not configured")
        
        enhanced_prompt = self._enhance_prompt(request)
        start_time = datetime.now()
        
        # Map our sizes to DALL-E supported sizes
        size_map = {
            ImageSize.SMALL: "1024x1024",
            ImageSize.MEDIUM: "1024x1024",
            ImageSize.LARGE: "1024x1024",
            ImageSize.WIDE: "1792x1024",
            ImageSize.TALL: "1024x1792",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "prompt": enhanced_prompt,
                    "n": 1,  # DALL-E 3 only supports n=1
                    "size": size_map.get(request.size, "1024x1024"),
                    "quality": "standard",
                    "response_format": "b64_json",
                },
                timeout=120.0,
            )
            
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", "Unknown error")
                raise RuntimeError(f"OpenAI API error: {error_msg}")
            
            result = response.json()
        
        end_time = datetime.now()
        generation_time = int((end_time - start_time).total_seconds() * 1000)
        
        images = []
        for i, img_data in enumerate(result.get("data", [])):
            image_bytes = base64.b64decode(img_data["b64_json"])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            images.append(GeneratedImage(
                image_data=image_bytes,
                filename=f"generated_{timestamp}_{i}.png",
                prompt_used=enhanced_prompt,
                generation_time_ms=generation_time,
                model_used=self.model,
                metadata={
                    "revised_prompt": img_data.get("revised_prompt", enhanced_prompt),
                    "size": size_map.get(request.size),
                },
            ))
        
        return images


class StabilityAIGenerator(ImageGeneratorBackend):
    """
    Stability AI (Stable Diffusion) backend.
    Uses the Stability AI API for image generation.
    """
    
    def __init__(self):
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.base_url = "https://api.stability.ai/v1/generation"
        self.engine = "stable-diffusion-xl-1024-v1-0"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def generate(self, request: GenerationRequest) -> List[GeneratedImage]:
        """Generate images using Stability AI."""
        if not self.is_available():
            raise RuntimeError("Stability AI API key not configured")
        
        start_time = datetime.now()
        
        # Build the prompt
        prompt = request.prompt
        if request.style_prompt:
            prompt = f"{prompt}, {request.style_prompt}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{self.engine}/text-to-image",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json={
                    "text_prompts": [
                        {"text": prompt, "weight": 1.0},
                        {"text": request.negative_prompt or "blurry, low quality", "weight": -1.0},
                    ],
                    "cfg_scale": 7,
                    "height": 1024,
                    "width": 1024,
                    "samples": request.num_images,
                    "steps": 30,
                },
                timeout=120.0,
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Stability AI error: {response.text}")
            
            result = response.json()
        
        end_time = datetime.now()
        generation_time = int((end_time - start_time).total_seconds() * 1000)
        
        images = []
        for i, artifact in enumerate(result.get("artifacts", [])):
            image_bytes = base64.b64decode(artifact["base64"])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            images.append(GeneratedImage(
                image_data=image_bytes,
                filename=f"stability_{timestamp}_{i}.png",
                prompt_used=prompt,
                generation_time_ms=generation_time,
                model_used=self.engine,
                metadata={"finish_reason": artifact.get("finishReason")},
            ))
        
        return images


class PlaceholderGenerator(ImageGeneratorBackend):
    """
    Placeholder image generator for testing/fallback.
    Generates simple colored placeholder images.
    """
    
    def is_available(self) -> bool:
        return True  # Always available as fallback
    
    async def generate(self, request: GenerationRequest) -> List[GeneratedImage]:
        """Generate a placeholder image."""
        from PIL import Image, ImageDraw, ImageFont
        
        # Parse size
        width, height = map(int, request.size.value.split("x"))
        
        # Create a gradient background
        img = Image.new("RGB", (width, height), color=(240, 240, 245))
        draw = ImageDraw.Draw(img)
        
        # Add some visual interest
        for i in range(0, width, 20):
            opacity = int(255 * (i / width) * 0.1)
            draw.line([(i, 0), (i, height)], fill=(200, 200, 210), width=1)
        
        # Add text
        text = f"[Generated Image]\n{request.prompt[:50]}..."
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Center the text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=(100, 100, 120), font=font)
        
        # Save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return [GeneratedImage(
            image_data=image_bytes,
            filename=f"placeholder_{timestamp}.png",
            prompt_used=request.prompt,
            generation_time_ms=50,
            model_used="placeholder",
            metadata={"type": "placeholder"},
        )]


class ImageGenerator:
    """
    Main image generation service.
    Automatically selects the best available backend.
    """
    
    def __init__(self, preferred_backend: str = "auto"):
        """
        Initialize the image generator.
        
        Args:
            preferred_backend: "openai", "stability", "placeholder", or "auto"
        """
        self.backends = {
            "openai": OpenAIImageGenerator(),
            "stability": StabilityAIGenerator(),
            "placeholder": PlaceholderGenerator(),
        }
        self.preferred_backend = preferred_backend
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)
    
    def _select_backend(self) -> ImageGeneratorBackend:
        """Select the best available backend."""
        if self.preferred_backend != "auto":
            backend = self.backends.get(self.preferred_backend)
            if backend and backend.is_available():
                return backend
        
        # Auto-select: prefer OpenAI, then Stability, then Placeholder
        for name in ["openai", "stability", "placeholder"]:
            backend = self.backends[name]
            if backend.is_available():
                logger.info(f"Using {name} backend for image generation")
                return backend
        
        raise RuntimeError("No image generation backend available")
    
    async def generate(
        self,
        prompt: str,
        style_prompt: str = "",
        size: ImageSize = ImageSize.LARGE,
        style: ImageStyle = ImageStyle.NATURAL,
        save_to_disk: bool = True,
    ) -> GeneratedImage:
        """
        Generate an image.
        
        Args:
            prompt: The image description
            style_prompt: Additional style from Style Gene
            size: Image dimensions
            style: Style preset
            save_to_disk: Whether to save the image file
            
        Returns:
            GeneratedImage with the result
        """
        request = GenerationRequest(
            prompt=prompt,
            style_prompt=style_prompt,
            size=size,
            style=style,
        )
        
        backend = self._select_backend()
        images = await backend.generate(request)
        
        if not images:
            raise RuntimeError("No images generated")
        
        image = images[0]
        
        if save_to_disk:
            file_path = self.output_dir / image.filename
            with open(file_path, "wb") as f:
                f.write(image.image_data)
            image.metadata["saved_path"] = str(file_path)
        
        return image
    
    async def generate_for_slide(
        self,
        visual_prompt: str,
        style_gene_prompt: str = "",
        visual_type: str = "image",
    ) -> GeneratedImage:
        """
        Generate an image for a presentation slide.
        
        Args:
            visual_prompt: Description from the NLP service
            style_gene_prompt: Style prompt from the Style Gene
            visual_type: Type of visual (image, icon, background)
            
        Returns:
            GeneratedImage suitable for embedding in a slide
        """
        # Enhance prompt based on visual type
        type_enhancements = {
            "image": "high quality illustration, presentation graphic",
            "icon": "simple icon, flat design, centered, white background",
            "background": "abstract background, subtle pattern, presentation backdrop",
        }
        
        enhanced = f"{visual_prompt}, {type_enhancements.get(visual_type, '')}"
        if style_gene_prompt:
            enhanced = f"{enhanced}, {style_gene_prompt}"
        
        return await self.generate(
            prompt=enhanced,
            size=ImageSize.LARGE if visual_type == "background" else ImageSize.MEDIUM,
            style=ImageStyle.CORPORATE,
        )
    
    def get_available_backends(self) -> List[str]:
        """Return list of available backends."""
        return [name for name, backend in self.backends.items() if backend.is_available()]


# Convenience functions
async def generate_image(prompt: str, style: str = "") -> GeneratedImage:
    """Quick function to generate an image."""
    generator = ImageGenerator()
    return await generator.generate(prompt, style_prompt=style)


async def generate_slide_visual(prompt: str, style_prompt: str = "") -> GeneratedImage:
    """Generate a visual for a slide."""
    generator = ImageGenerator()
    return await generator.generate_for_slide(prompt, style_prompt)
