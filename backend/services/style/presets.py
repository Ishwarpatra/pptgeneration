"""
Pre-defined Style Gene presets.
These serve as 'parent' styles that can be bred together.
"""
from .style_gene import (
    StyleGene,
    TypographyParams,
    ColorPalette,
    LayoutPhysics,
    FontWeight,
)


# Corporate Professional
CORPORATE_CLASSIC = StyleGene(
    gene_id="corporate_classic",
    name="Corporate Classic",
    typography=TypographyParams(
        heading_font="Georgia",
        body_font="Arial",
        heading_weight=FontWeight.BOLD,
        base_size_pt=14.0,
        scale_ratio=1.2,
    ),
    palette=ColorPalette.from_hex_dict({
        "primary": "#1e3a5f",
        "secondary": "#2c5282",
        "accent": "#c05621",
        "background": "#ffffff",
        "surface": "#f7fafc",
        "text_primary": "#1a202c",
        "text_secondary": "#4a5568",
    }),
    layout=LayoutPhysics(
        density=0.5,
        corner_radius=4.0,
        margin_factor=0.08,
        shadow_intensity=0.05,
    ),
    visual_style_prompt="professional corporate, business presentation, clean navy blue, formal",
    tags=["corporate", "professional", "formal", "business"],
)


# Modern Minimalist
MODERN_MINIMAL = StyleGene(
    gene_id="modern_minimal",
    name="Modern Minimal",
    typography=TypographyParams(
        heading_font="Inter",
        body_font="Inter",
        heading_weight=FontWeight.SEMIBOLD,
        base_size_pt=16.0,
        scale_ratio=1.333,
        line_height=1.6,
    ),
    palette=ColorPalette.from_hex_dict({
        "primary": "#18181b",
        "secondary": "#3f3f46",
        "accent": "#2563eb",
        "background": "#fafafa",
        "surface": "#ffffff",
        "text_primary": "#09090b",
        "text_secondary": "#71717a",
    }),
    layout=LayoutPhysics(
        density=0.3,
        corner_radius=12.0,
        margin_factor=0.1,
        shadow_intensity=0.0,
    ),
    visual_style_prompt="minimal clean modern, lots of whitespace, subtle, elegant",
    tags=["minimal", "modern", "clean", "simple"],
)


# Tech Startup
TECH_STARTUP = StyleGene(
    gene_id="tech_startup",
    name="Tech Startup",
    typography=TypographyParams(
        heading_font="Poppins",
        body_font="Inter",
        heading_weight=FontWeight.BOLD,
        base_size_pt=15.0,
        scale_ratio=1.25,
    ),
    palette=ColorPalette.from_hex_dict({
        "primary": "#6366f1",
        "secondary": "#8b5cf6",
        "accent": "#06b6d4",
        "background": "#ffffff",
        "surface": "#f5f3ff",
        "text_primary": "#1e1b4b",
        "text_secondary": "#6b7280",
    }),
    layout=LayoutPhysics(
        density=0.4,
        corner_radius=16.0,
        margin_factor=0.06,
        shadow_intensity=0.15,
    ),
    visual_style_prompt="tech startup, gradient, vibrant purple blue, modern SaaS, innovative",
    tags=["tech", "startup", "modern", "vibrant", "gradient"],
)


# Dark Mode Cyber
DARK_CYBER = StyleGene(
    gene_id="dark_cyber",
    name="Dark Cyber",
    typography=TypographyParams(
        heading_font="Roboto Mono",
        body_font="Roboto",
        heading_weight=FontWeight.BOLD,
        base_size_pt=14.0,
        scale_ratio=1.2,
    ),
    palette=ColorPalette.from_hex_dict({
        "primary": "#00ff88",
        "secondary": "#00d4ff",
        "accent": "#ff00ff",
        "background": "#0a0a0f",
        "surface": "#141420",
        "text_primary": "#e4e4e7",
        "text_secondary": "#a1a1aa",
    }),
    layout=LayoutPhysics(
        density=0.45,
        corner_radius=8.0,
        margin_factor=0.05,
        shadow_intensity=0.0,
        border_width=1.0,
    ),
    visual_style_prompt="cyberpunk, neon glow, dark mode, futuristic, matrix grid, tech noir",
    tags=["dark", "cyber", "neon", "futuristic", "tech"],
)


# Creative Bold
CREATIVE_BOLD = StyleGene(
    gene_id="creative_bold",
    name="Creative Bold",
    typography=TypographyParams(
        heading_font="Playfair Display",
        body_font="Source Sans Pro",
        heading_weight=FontWeight.BOLD,
        base_size_pt=16.0,
        scale_ratio=1.414,  # Augmented fourth
    ),
    palette=ColorPalette.from_hex_dict({
        "primary": "#dc2626",
        "secondary": "#ea580c",
        "accent": "#fbbf24",
        "background": "#fffbeb",
        "surface": "#ffffff",
        "text_primary": "#1c1917",
        "text_secondary": "#57534e",
    }),
    layout=LayoutPhysics(
        density=0.5,
        corner_radius=0.0,  # Sharp edges
        margin_factor=0.07,
        shadow_intensity=0.2,
    ),
    visual_style_prompt="bold creative, artistic, warm colors, expressive, dynamic, energetic",
    tags=["creative", "bold", "artistic", "warm", "energetic"],
)


# Nature Organic
NATURE_ORGANIC = StyleGene(
    gene_id="nature_organic",
    name="Nature Organic",
    typography=TypographyParams(
        heading_font="Lora",
        body_font="Open Sans",
        heading_weight=FontWeight.MEDIUM,
        base_size_pt=15.0,
        scale_ratio=1.25,
        line_height=1.7,
    ),
    palette=ColorPalette.from_hex_dict({
        "primary": "#166534",
        "secondary": "#15803d",
        "accent": "#84cc16",
        "background": "#f0fdf4",
        "surface": "#ffffff",
        "text_primary": "#14532d",
        "text_secondary": "#4d7c0f",
    }),
    layout=LayoutPhysics(
        density=0.35,
        corner_radius=24.0,  # Very rounded
        margin_factor=0.09,
        shadow_intensity=0.08,
    ),
    visual_style_prompt="organic nature, green sustainable, eco-friendly, natural, peaceful",
    tags=["nature", "organic", "green", "sustainable", "calm"],
)


# All presets dictionary
STYLE_PRESETS = {
    "corporate_classic": CORPORATE_CLASSIC,
    "modern_minimal": MODERN_MINIMAL,
    "tech_startup": TECH_STARTUP,
    "dark_cyber": DARK_CYBER,
    "creative_bold": CREATIVE_BOLD,
    "nature_organic": NATURE_ORGANIC,
}


def get_preset(preset_id: str) -> StyleGene:
    """Get a style preset by ID."""
    if preset_id not in STYLE_PRESETS:
        raise ValueError(f"Unknown preset: {preset_id}. Available: {list(STYLE_PRESETS.keys())}")
    return STYLE_PRESETS[preset_id]


def list_presets() -> list:
    """List all available preset metadata."""
    return [
        {
            "id": gene.gene_id,
            "name": gene.name,
            "tags": gene.tags,
            "preview_colors": gene.palette.to_hex_dict(),
        }
        for gene in STYLE_PRESETS.values()
    ]


def breed_styles(
    parent_a_id: str,
    parent_b_id: str,
    alpha: float = 0.5
) -> StyleGene:
    """
    Breed two preset styles together.
    
    Args:
        parent_a_id: First parent preset ID
        parent_b_id: Second parent preset ID
        alpha: Mixing factor (0.0 = 100% A, 1.0 = 100% B)
        
    Returns:
        New child StyleGene
    """
    parent_a = get_preset(parent_a_id)
    parent_b = get_preset(parent_b_id)
    return parent_a.interpolate(parent_b, alpha)
