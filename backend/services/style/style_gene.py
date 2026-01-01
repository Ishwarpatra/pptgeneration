"""
Style Gene Data Structures.
Parametric representation of visual themes for "breeding" and mixing.

Uses the 'colormath' library for accurate, battle-tested color space conversions.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
import logging

# Import colormath for professional color space conversions
try:
    from colormath.color_objects import sRGBColor, LabColor
    from colormath.color_conversions import convert_color
    COLORMATH_AVAILABLE = True
except ImportError:
    COLORMATH_AVAILABLE = False
    logging.warning(
        "colormath library not installed. Install with 'pip install colormath' "
        "for accurate color space conversions. Falling back to approximation."
    )

logger = logging.getLogger(__name__)


class FontWeight(str, Enum):
    LIGHT = "300"
    REGULAR = "400"
    MEDIUM = "500"
    SEMIBOLD = "600"
    BOLD = "700"


@dataclass
class TypographyParams:
    """Typography parameters for a style."""
    heading_font: str = "Inter"
    body_font: str = "Inter"
    heading_weight: FontWeight = FontWeight.BOLD
    body_weight: FontWeight = FontWeight.REGULAR
    base_size_pt: float = 16.0
    scale_ratio: float = 1.25  # Modular scale ratio (H1/H2/H3)
    line_height: float = 1.5
    letter_spacing: float = 0.0

    def get_heading_sizes(self) -> dict:
        """Calculate heading sizes using modular scale."""
        return {
            "h1": self.base_size_pt * (self.scale_ratio ** 4),
            "h2": self.base_size_pt * (self.scale_ratio ** 3),
            "h3": self.base_size_pt * (self.scale_ratio ** 2),
            "h4": self.base_size_pt * self.scale_ratio,
            "body": self.base_size_pt,
        }


@dataclass
class LABColor:
    """
    Color in CIELAB color space.
    LAB provides perceptually uniform color interpolation.
    
    Uses 'colormath' library when available for accurate conversions,
    with a fallback approximation for environments without it.
    """
    L: float  # Lightness (0-100)
    a: float  # Green-Red axis (-128 to 127)
    b: float  # Blue-Yellow axis (-128 to 127)

    @classmethod
    def from_hex(cls, hex_color: str) -> "LABColor":
        """Convert hex color to LAB using colormath library."""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        
        if COLORMATH_AVAILABLE:
            # Use colormath for accurate conversion
            rgb = sRGBColor(r, g, b)
            lab = convert_color(rgb, LabColor)
            return cls(L=lab.lab_l, a=lab.lab_a, b=lab.lab_b)
        else:
            # Fallback: Approximate conversion
            return cls._from_hex_fallback(r, g, b)
    
    @classmethod
    def _from_hex_fallback(cls, r: float, g: float, b: float) -> "LABColor":
        """Fallback RGB to LAB conversion when colormath is unavailable."""
        # RGB to XYZ (D65 illuminant)
        def gamma_correct(c):
            return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
        
        r, g, b = gamma_correct(r), gamma_correct(g), gamma_correct(b)
        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        
        # XYZ to LAB
        xn, yn, zn = 0.95047, 1.0, 1.08883
        
        def f(t):
            return t ** (1/3) if t > 0.008856 else 7.787 * t + 16/116
        
        L = 116 * f(y/yn) - 16
        a = 500 * (f(x/xn) - f(y/yn))
        b_val = 200 * (f(y/yn) - f(z/zn))
        
        return cls(L=L, a=a, b=b_val)

    def to_hex(self) -> str:
        """Convert LAB to hex color using colormath library."""
        if COLORMATH_AVAILABLE:
            # Use colormath for accurate conversion
            lab = LabColor(self.L, self.a, self.b)
            rgb = convert_color(lab, sRGBColor)
            # Clamp values to valid range
            r = max(0, min(1, rgb.rgb_r))
            g = max(0, min(1, rgb.rgb_g))
            b = max(0, min(1, rgb.rgb_b))
            return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        else:
            # Fallback conversion
            return self._to_hex_fallback()
    
    def _to_hex_fallback(self) -> str:
        """Fallback LAB to hex conversion when colormath is unavailable."""
        # LAB to XYZ
        def f_inv(t):
            return t ** 3 if t > 0.206893 else (t - 16/116) / 7.787
        
        xn, yn, zn = 0.95047, 1.0, 1.08883
        y = yn * f_inv((self.L + 16) / 116)
        x = xn * f_inv((self.L + 16) / 116 + self.a / 500)
        z = zn * f_inv((self.L + 16) / 116 - self.b / 200)
        
        # XYZ to RGB
        r = x * 3.2404542 - y * 1.5371385 - z * 0.4985314
        g = -x * 0.9692660 + y * 1.8760108 + z * 0.0415560
        b = x * 0.0556434 - y * 0.2040259 + z * 1.0572252
        
        def gamma_expand(c):
            return 1.055 * (c ** (1/2.4)) - 0.055 if c > 0.0031308 else 12.92 * c
        
        r = max(0, min(1, gamma_expand(r)))
        g = max(0, min(1, gamma_expand(g)))
        b = max(0, min(1, gamma_expand(b)))
        
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def interpolate(self, other: "LABColor", alpha: float) -> "LABColor":
        """Linearly interpolate between two LAB colors."""
        return LABColor(
            L=self.L * (1 - alpha) + other.L * alpha,
            a=self.a * (1 - alpha) + other.a * alpha,
            b=self.b * (1 - alpha) + other.b * alpha,
        )


@dataclass
class ColorPalette:
    """Color palette with LAB color support for smooth interpolation."""
    primary: LABColor
    secondary: LABColor
    accent: LABColor
    background: LABColor
    surface: LABColor
    text_primary: LABColor
    text_secondary: LABColor

    @classmethod
    def from_hex_dict(cls, colors: dict) -> "ColorPalette":
        """Create palette from hex color dictionary."""
        return cls(
            primary=LABColor.from_hex(colors.get("primary", "#2563eb")),
            secondary=LABColor.from_hex(colors.get("secondary", "#7c3aed")),
            accent=LABColor.from_hex(colors.get("accent", "#f59e0b")),
            background=LABColor.from_hex(colors.get("background", "#ffffff")),
            surface=LABColor.from_hex(colors.get("surface", "#f8fafc")),
            text_primary=LABColor.from_hex(colors.get("text_primary", "#1e293b")),
            text_secondary=LABColor.from_hex(colors.get("text_secondary", "#64748b")),
        )

    def to_hex_dict(self) -> dict:
        """Export palette as hex colors."""
        return {
            "primary": self.primary.to_hex(),
            "secondary": self.secondary.to_hex(),
            "accent": self.accent.to_hex(),
            "background": self.background.to_hex(),
            "surface": self.surface.to_hex(),
            "text_primary": self.text_primary.to_hex(),
            "text_secondary": self.text_secondary.to_hex(),
        }

    def interpolate(self, other: "ColorPalette", alpha: float) -> "ColorPalette":
        """Interpolate between two palettes in LAB space."""
        return ColorPalette(
            primary=self.primary.interpolate(other.primary, alpha),
            secondary=self.secondary.interpolate(other.secondary, alpha),
            accent=self.accent.interpolate(other.accent, alpha),
            background=self.background.interpolate(other.background, alpha),
            surface=self.surface.interpolate(other.surface, alpha),
            text_primary=self.text_primary.interpolate(other.text_primary, alpha),
            text_secondary=self.text_secondary.interpolate(other.text_secondary, alpha),
        )


@dataclass
class LayoutPhysics:
    """Layout parameters controlling spacing and shapes."""
    density: float = 0.4  # 0.0 (minimal) to 1.0 (dense)
    corner_radius: float = 8.0  # px
    margin_factor: float = 0.08  # As fraction of slide width
    padding_factor: float = 0.04
    shadow_intensity: float = 0.1  # 0.0 to 1.0
    border_width: float = 0.0

    def interpolate(self, other: "LayoutPhysics", alpha: float) -> "LayoutPhysics":
        """Linear interpolation of layout parameters."""
        return LayoutPhysics(
            density=self._lerp(self.density, other.density, alpha),
            corner_radius=self._lerp(self.corner_radius, other.corner_radius, alpha),
            margin_factor=self._lerp(self.margin_factor, other.margin_factor, alpha),
            padding_factor=self._lerp(self.padding_factor, other.padding_factor, alpha),
            shadow_intensity=self._lerp(self.shadow_intensity, other.shadow_intensity, alpha),
            border_width=self._lerp(self.border_width, other.border_width, alpha),
        )

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        """Linear interpolation."""
        return a * (1 - t) + b * t


@dataclass
class StyleGene:
    """
    Complete parametric representation of a visual theme.
    The 'DNA' that can be bred and mixed Artbreeder-style.
    """
    gene_id: str
    name: str
    typography: TypographyParams = field(default_factory=TypographyParams)
    palette: ColorPalette = field(default_factory=lambda: ColorPalette.from_hex_dict({}))
    layout: LayoutPhysics = field(default_factory=LayoutPhysics)
    visual_style_prompt: str = "professional, clean, modern"
    tags: List[str] = field(default_factory=list)

    def interpolate(self, other: "StyleGene", alpha: float) -> "StyleGene":
        """
        Breed two Style Genes together.
        
        Args:
            other: The other parent style
            alpha: Mixing factor (0.0 = 100% self, 1.0 = 100% other)
            
        Returns:
            A new child StyleGene
        """
        # Interpolate numeric parameters
        new_typography = TypographyParams(
            heading_font=self.typography.heading_font if alpha < 0.5 else other.typography.heading_font,
            body_font=self.typography.body_font if alpha < 0.5 else other.typography.body_font,
            heading_weight=self.typography.heading_weight if alpha < 0.5 else other.typography.heading_weight,
            body_weight=self.typography.body_weight if alpha < 0.5 else other.typography.body_weight,
            base_size_pt=LayoutPhysics._lerp(
                self.typography.base_size_pt, 
                other.typography.base_size_pt, 
                alpha
            ),
            scale_ratio=LayoutPhysics._lerp(
                self.typography.scale_ratio,
                other.typography.scale_ratio,
                alpha
            ),
            line_height=LayoutPhysics._lerp(
                self.typography.line_height,
                other.typography.line_height,
                alpha
            ),
        )

        # Combine visual prompts with weighted attention
        weight_self = 1.0 - alpha
        weight_other = alpha
        combined_prompt = f"({self.visual_style_prompt}:{weight_self:.1f}) AND ({other.visual_style_prompt}:{weight_other:.1f})"

        return StyleGene(
            gene_id=f"{self.gene_id}_x_{other.gene_id}_{int(alpha*100)}",
            name=f"{self.name} × {other.name}",
            typography=new_typography,
            palette=self.palette.interpolate(other.palette, alpha),
            layout=self.layout.interpolate(other.layout, alpha),
            visual_style_prompt=combined_prompt,
            tags=list(set(self.tags + other.tags)),
        )

    def to_css_variables(self) -> dict:
        """Export style as CSS custom properties."""
        colors = self.palette.to_hex_dict()
        sizes = self.typography.get_heading_sizes()
        
        return {
            # Colors
            "--color-primary": colors["primary"],
            "--color-secondary": colors["secondary"],
            "--color-accent": colors["accent"],
            "--color-background": colors["background"],
            "--color-surface": colors["surface"],
            "--color-text": colors["text_primary"],
            "--color-text-muted": colors["text_secondary"],
            
            # Typography
            "--font-heading": self.typography.heading_font,
            "--font-body": self.typography.body_font,
            "--font-size-h1": f"{sizes['h1']:.1f}pt",
            "--font-size-h2": f"{sizes['h2']:.1f}pt",
            "--font-size-h3": f"{sizes['h3']:.1f}pt",
            "--font-size-body": f"{sizes['body']:.1f}pt",
            "--line-height": str(self.typography.line_height),
            
            # Layout
            "--border-radius": f"{self.layout.corner_radius}px",
            "--shadow-opacity": str(self.layout.shadow_intensity),
        }

    def to_dict(self) -> dict:
        """Serialize to dictionary for storage/API."""
        return {
            "gene_id": self.gene_id,
            "name": self.name,
            "typography": {
                "heading_font": self.typography.heading_font,
                "body_font": self.typography.body_font,
                "base_size_pt": self.typography.base_size_pt,
                "scale_ratio": self.typography.scale_ratio,
            },
            "palette": self.palette.to_hex_dict(),
            "layout": {
                "density": self.layout.density,
                "corner_radius": self.layout.corner_radius,
                "margin_factor": self.layout.margin_factor,
            },
            "visual_style_prompt": self.visual_style_prompt,
            "tags": self.tags,
        }
