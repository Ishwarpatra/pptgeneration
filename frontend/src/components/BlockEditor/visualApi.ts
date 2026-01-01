// Visual Synthesis API Service
// Handles communication with the backend image generation service

import { API_ENDPOINTS, apiFetch, API_BASE_URL } from '../../config/api';

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

export const visualApi = {
    /**
     * Get available image styles from the backend
     */
    async getStyles(): Promise<{ styles: ImageStyle[] }> {
        return apiFetch(API_ENDPOINTS.visual.styles);
    },

    /**
     * Generate an AI image
     */
    async generateImage(request: ImageGenerationRequest): Promise<ImageGenerationResponse> {
        return apiFetch(API_ENDPOINTS.visual.generate, {
            method: 'POST',
            body: JSON.stringify(request),
        });
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

        const response = await fetch(`${API_ENDPOINTS.visual.suggest}?${params}`, {
            method: 'POST',
        });

        if (!response.ok) throw new Error('Failed to get suggestions');
        return response.json();
    },

    /**
     * Get the URL for a generated image
     */
    getImageUrl(filename: string): string {
        return API_ENDPOINTS.visual.image(filename);
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
        return apiFetch(API_ENDPOINTS.visual.provider);
    }
};

// Export the API base for direct access if needed
export { API_BASE_URL };

export default visualApi;
