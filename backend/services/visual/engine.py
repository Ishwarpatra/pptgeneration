# Visual Synthesis Engine
# AI Image generation service supporting multiple providers
import os
import httpx
import base64
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageStyle,
    ImageSuggestion,
    SlideImageAnalysis,
    AspectRatio
)


class VisualSynthesisEngine:
    """
    AI Image Generation Engine for Presentation Slides
    
    Supports multiple providers:
    - OpenAI DALL-E 3
    - Stability AI
    - Local placeholder generation (for development)
    """
    
    STYLE_PROMPTS = {
        ImageStyle.PHOTOREALISTIC: "photorealistic, high detail, professional photography, 8k",
        ImageStyle.ILLUSTRATION: "digital illustration, vibrant colors, clean lines, artistic",
        ImageStyle.FLAT_DESIGN: "flat design, minimal shadows, solid colors, modern UI style",
        ImageStyle.ISOMETRIC: "isometric 3D illustration, geometric, clean perspective",
        ImageStyle.WATERCOLOR: "watercolor painting style, soft edges, artistic blend",
        ImageStyle.MINIMALIST: "minimalist, simple shapes, lots of white space, clean",
        ImageStyle.CORPORATE: "professional, business, corporate style, clean and modern",
        ImageStyle.ABSTRACT: "abstract art, shapes, gradients, creative composition",
        ImageStyle.INFOGRAPHIC: "infographic style, data visualization, icons, clear layout",
        ImageStyle.ICON: "simple icon, flat design, single color, minimal detail",
    }
    
    ASPECT_DIMENSIONS = {
        AspectRatio.WIDESCREEN: (1792, 1024),  # 16:9 equivalent for DALL-E
        AspectRatio.STANDARD: (1024, 768),      # 4:3
        AspectRatio.SQUARE: (1024, 1024),       # 1:1
        AspectRatio.PORTRAIT: (1024, 1792),     # 9:16
    }
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)
        
        # Select provider based on available API keys
        if self.openai_api_key:
            self.provider = "openai"
        elif self.stability_api_key:
            self.provider = "stability"
        else:
            self.provider = "placeholder"
    
    def _enhance_prompt(self, request: ImageGenerationRequest) -> str:
        """Enhance user prompt with style modifiers for better results"""
        base_prompt = request.prompt
        style_modifier = self.STYLE_PROMPTS.get(request.style, "")
        
        # Add color palette if specified
        color_modifier = ""
        if request.color_palette:
            colors = ", ".join(request.color_palette[:3])  # Limit to 3 colors
            color_modifier = f"using colors: {colors}"
        
        # Add context
        context_modifier = ""
        if request.slide_context:
            context_modifier = f"for a presentation about {request.slide_context}"
        
        # Presentation-specific enhancements
        presentation_modifier = "suitable for business presentation, clean background, high contrast"
        
        # Combine all parts
        enhanced = f"{base_prompt}, {style_modifier}, {color_modifier}, {context_modifier}, {presentation_modifier}"
        
        # Add negative prompt handling
        if request.negative_prompt:
            enhanced += f". Avoid: {request.negative_prompt}"
        
        return enhanced.strip(", ")
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate an image using the configured provider"""
        enhanced_prompt = self._enhance_prompt(request)
        
        try:
            if self.provider == "openai":
                return await self._generate_with_openai(request, enhanced_prompt)
            elif self.provider == "stability":
                return await self._generate_with_stability(request, enhanced_prompt)
            else:
                return await self._generate_placeholder(request, enhanced_prompt)
        except Exception as e:
            return ImageGenerationResponse(
                success=False,
                prompt_used=enhanced_prompt,
                style=request.style,
                error=str(e),
                credits_used=0
            )
    
    async def _generate_with_openai(
        self, 
        request: ImageGenerationRequest, 
        enhanced_prompt: str
    ) -> ImageGenerationResponse:
        """Generate image using OpenAI DALL-E 3"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Map quality to DALL-E parameter
            quality_map = {"draft": "standard", "standard": "standard", "high": "hd"}
            dalle_quality = quality_map.get(request.quality, "standard")
            
            # DALL-E 3 only supports specific sizes
            if request.aspect_ratio == AspectRatio.WIDESCREEN:
                size = "1792x1024"
            elif request.aspect_ratio == AspectRatio.PORTRAIT:
                size = "1024x1792"
            else:
                size = "1024x1024"
            
            response = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": enhanced_prompt,
                    "n": 1,
                    "size": size,
                    "quality": dalle_quality,
                    "response_format": "url"
                }
            )
            
            if response.status_code != 200:
                error_data = response.json()
                raise Exception(f"DALL-E API error: {error_data.get('error', {}).get('message', 'Unknown error')}")
            
            data = response.json()
            image_url = data["data"][0]["url"]
            
            # Download and save locally
            local_path = await self._download_image(image_url)
            
            return ImageGenerationResponse(
                success=True,
                image_url=image_url,
                image_path=str(local_path),
                prompt_used=enhanced_prompt,
                style=request.style,
                credits_used=1 if request.quality != "high" else 2
            )
    
    async def _generate_with_stability(
        self,
        request: ImageGenerationRequest,
        enhanced_prompt: str
    ) -> ImageGenerationResponse:
        """Generate image using Stability AI"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            width, height = self.ASPECT_DIMENSIONS.get(
                request.aspect_ratio, 
                (1024, 1024)
            )
            
            response = await client.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Authorization": f"Bearer {self.stability_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json={
                    "text_prompts": [
                        {"text": enhanced_prompt, "weight": 1.0},
                        {"text": request.negative_prompt or "blurry, low quality, text, watermark", "weight": -1.0}
                    ],
                    "cfg_scale": 7,
                    "width": width,
                    "height": height,
                    "samples": 1,
                    "steps": 30 if request.quality == "high" else 20
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Stability API error: {response.text}")
            
            data = response.json()
            image_b64 = data["artifacts"][0]["base64"]
            
            # Save locally
            local_path = self._save_base64_image(image_b64)
            
            return ImageGenerationResponse(
                success=True,
                image_path=str(local_path),
                prompt_used=enhanced_prompt,
                style=request.style,
                credits_used=1
            )
    
    async def _generate_placeholder(
        self,
        request: ImageGenerationRequest,
        enhanced_prompt: str
    ) -> ImageGenerationResponse:
        """Generate a placeholder image for development/testing"""
        # Create a simple SVG placeholder
        width, height = self.ASPECT_DIMENSIONS.get(
            request.aspect_ratio,
            (1024, 576)
        )
        
        # Style-based colors
        style_colors = {
            ImageStyle.CORPORATE: ("#1e3a5f", "#ffffff"),
            ImageStyle.MINIMALIST: ("#f5f5f5", "#333333"),
            ImageStyle.ABSTRACT: ("#8b5cf6", "#ffffff"),
            ImageStyle.PHOTOREALISTIC: ("#2c3e50", "#ecf0f1"),
            ImageStyle.ILLUSTRATION: ("#e74c3c", "#ffffff"),
        }
        bg_color, text_color = style_colors.get(request.style, ("#333333", "#ffffff"))
        
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
            <defs>
                <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:{bg_color};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:{bg_color}88;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#grad)"/>
            <text x="50%" y="45%" font-family="Arial, sans-serif" font-size="24" 
                  fill="{text_color}" text-anchor="middle" opacity="0.8">
                🎨 AI Generated Image
            </text>
            <text x="50%" y="55%" font-family="Arial, sans-serif" font-size="14" 
                  fill="{text_color}" text-anchor="middle" opacity="0.6">
                {request.style.value} | {request.aspect_ratio.value}
            </text>
        </svg>'''
        
        # Save SVG
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"placeholder_{timestamp}.svg"
        filepath = self.output_dir / filename
        
        with open(filepath, "w") as f:
            f.write(svg_content)
        
        return ImageGenerationResponse(
            success=True,
            image_path=str(filepath),
            prompt_used=enhanced_prompt,
            style=request.style,
            credits_used=0  # Placeholders are free
        )
    
    async def _download_image(self, url: str) -> Path:
        """Download image from URL and save locally"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}.png"
            filepath = self.output_dir / filename
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            return filepath
    
    def _save_base64_image(self, b64_data: str) -> Path:
        """Save base64 encoded image"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.png"
        filepath = self.output_dir / filename
        
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(b64_data))
        
        return filepath
    
    async def suggest_images_for_slide(
        self,
        slide_title: str,
        slide_content: str,
        style_preference: Optional[ImageStyle] = None
    ) -> SlideImageAnalysis:
        """
        Analyze slide content and suggest appropriate images
        Uses LLM to understand context and suggest relevant visuals
        """
        # Smart suggestion logic based on content analysis
        suggestions = []
        
        # Keywords that suggest image types
        concept_keywords = {
            "data": (ImageStyle.INFOGRAPHIC, "data visualization chart"),
            "growth": (ImageStyle.CORPORATE, "upward growth arrow or graph"),
            "team": (ImageStyle.PHOTOREALISTIC, "diverse professional team collaboration"),
            "technology": (ImageStyle.ISOMETRIC, "modern technology devices and interfaces"),
            "innovation": (ImageStyle.ABSTRACT, "abstract innovation concept with light bulbs"),
            "nature": (ImageStyle.WATERCOLOR, "nature landscape scene"),
            "success": (ImageStyle.CORPORATE, "business success achievement celebration"),
            "global": (ImageStyle.FLAT_DESIGN, "global network world map connections"),
            "ai": (ImageStyle.ABSTRACT, "artificial intelligence neural network visualization"),
            "cloud": (ImageStyle.ISOMETRIC, "cloud computing infrastructure"),
        }
        
        combined_text = f"{slide_title} {slide_content}".lower()
        
        for keyword, (style, prompt) in concept_keywords.items():
            if keyword in combined_text:
                suggestions.append(ImageSuggestion(
                    suggested_prompt=f"{prompt}, related to {slide_title}",
                    confidence=0.8 if keyword in slide_title.lower() else 0.6,
                    style=style_preference or style,
                    rationale=f"Content mentions '{keyword}' which suggests this visual"
                ))
        
        # Add a generic suggestion if none found
        if not suggestions:
            default_style = style_preference or ImageStyle.CORPORATE
            suggestions.append(ImageSuggestion(
                suggested_prompt=f"Professional illustration representing {slide_title}",
                confidence=0.5,
                style=default_style,
                rationale="Generic professional visual for the slide topic"
            ))
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        return SlideImageAnalysis(
            slide_title=slide_title,
            slide_content=slide_content[:200],
            suggestions=suggestions[:3],  # Top 3 suggestions
            recommended_count=1 if len(slide_content) < 100 else 2
        )


# Singleton instance
_engine: Optional[VisualSynthesisEngine] = None


def get_visual_engine() -> VisualSynthesisEngine:
    """Get or create the visual synthesis engine singleton"""
    global _engine
    if _engine is None:
        _engine = VisualSynthesisEngine()
    return _engine
