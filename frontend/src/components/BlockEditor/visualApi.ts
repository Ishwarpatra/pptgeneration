// Visual Synthesis API Service
// Handles communication with the backend image generation service

export interface ImageStyle {
    id: string;
    name: string;
    description: string;
}

export interface ImageGenerationRequest {
    prompt: string;
    style?: string;
    aspect_ratio?: string;
    negative_prompt?: string;
    color_palette?: string[];
    slide_context?: string;
    quality?: 'draft' | 'standard' | 'high';
}

export interface ImageGenerationResponse {
    success: boolean;
    image_url?: string;
    image_path?: string;
    prompt_used: string;
    style: string;
    error?: string;
    credits_used: number;
}

export interface ImageSuggestion {
    suggested_prompt: string;
    confidence: number;
    style: string;
    rationale: string;
}

export interface SlideImageAnalysis {
    slide_title: string;
    slide_content: string;
    suggestions: ImageSuggestion[];
    recommended_count: number;
}

const API_BASE = 'http://localhost:8000';

export const visualApi = {
    /**
     * Get available image styles
     */
    async getStyles(): Promise<{ styles: ImageStyle[] }> {
        const response = await fetch(`${API_BASE}/api/visual/styles`);
        if (!response.ok) throw new Error('Failed to fetch styles');
        return response.json();
    },

    /**
     * Generate an AI image
     */
    async generateImage(request: ImageGenerationRequest): Promise<ImageGenerationResponse> {
        const response = await fetch(`${API_BASE}/api/visual/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Image generation failed');
        }

        return response.json();
    },

    /**
     * Get image suggestions for slide content
     */
    async suggestImages(
        slideTitle: string,
        slideContent: string,
        stylePreference?: string
    ): Promise<SlideImageAnalysis> {
        const params = new URLSearchParams({
            slide_title: slideTitle,
            slide_content: slideContent,
        });

        if (stylePreference) {
            params.append('style_preference', stylePreference);
        }

        const response = await fetch(`${API_BASE}/api/visual/suggest?${params}`, {
            method: 'POST',
        });

        if (!response.ok) throw new Error('Failed to get suggestions');
        return response.json();
    },

    /**
     * Get the URL for a generated image
     */
    getImageUrl(filename: string): string {
        return `${API_BASE}/api/visual/image/${filename}`;
    },

    /**
     * Get current provider info
     */
    async getProviderInfo(): Promise<{
        current_provider: string;
        details: Record<string, string>;
        available_styles: number;
        available_ratios: number;
    }> {
        const response = await fetch(`${API_BASE}/api/visual/provider`);
        if (!response.ok) throw new Error('Failed to fetch provider info');
        return response.json();
    }
};

export default visualApi;
