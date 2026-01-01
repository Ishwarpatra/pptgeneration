/**
 * Presentations API Service
 * Handles all presentation-related API calls
 */

import { API_ENDPOINTS, apiFetch } from '../config/api';

export interface Presentation {
    id: string;
    title: string;
    thumbnail: string;
    createdAt: string;
    updatedAt?: string;
    isPrivate: boolean;
    author: string;
    isFavorite: boolean;
    slideCount?: number;
    styleId?: string;
}

export interface CreatePresentationRequest {
    topic: string;
    num_slides: number;
    style_id: string;
    context?: string;
}

export interface CreatePresentationResponse {
    success: boolean;
    presentation_id: string;
    file_path: string;
    download_url: string;
    slide_count: number;
}

export interface StylePreset {
    id: string;
    name: string;
    description: string;
    category: string;
    colors: string[];
    isPremium: boolean;
    thumbnail?: string;
    slideCount?: number;
}

export const presentationsApi = {
    /**
     * Fetch all presentations for the current user
     */
    async list(): Promise<Presentation[]> {
        try {
            return await apiFetch<Presentation[]>(API_ENDPOINTS.presentations.list);
        } catch (error) {
            console.error('Failed to fetch presentations:', error);
            // Return empty array on error (API might not be running yet)
            return [];
        }
    },

    /**
     * Get a single presentation by ID
     */
    async get(id: string): Promise<Presentation> {
        return apiFetch(API_ENDPOINTS.presentations.get(id));
    },

    /**
     * Generate a new presentation with AI
     */
    async generate(request: CreatePresentationRequest): Promise<CreatePresentationResponse> {
        return apiFetch(API_ENDPOINTS.presentations.generate, {
            method: 'POST',
            body: JSON.stringify(request),
        });
    },

    /**
     * Update presentation metadata
     */
    async update(id: string, data: Partial<Presentation>): Promise<Presentation> {
        return apiFetch(API_ENDPOINTS.presentations.update(id), {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    /**
     * Toggle favorite status
     */
    async toggleFavorite(id: string, isFavorite: boolean): Promise<Presentation> {
        return apiFetch(API_ENDPOINTS.presentations.update(id), {
            method: 'PATCH',
            body: JSON.stringify({ isFavorite }),
        });
    },

    /**
     * Delete a presentation
     */
    async delete(id: string): Promise<void> {
        await apiFetch(API_ENDPOINTS.presentations.delete(id), {
            method: 'DELETE',
        });
    },

    /**
     * Get download URL for a presentation
     */
    getDownloadUrl(id: string): string {
        return API_ENDPOINTS.presentations.download(id);
    },
};

export const stylesApi = {
    /**
     * Fetch available style presets from the backend
     */
    async getPresets(): Promise<StylePreset[]> {
        try {
            return await apiFetch<StylePreset[]>(API_ENDPOINTS.styles.presets);
        } catch (error) {
            console.error('Failed to fetch style presets:', error);
            // Return default presets on error
            return getDefaultPresets();
        }
    },

    /**
     * Get a specific style preset
     */
    async getPreset(id: string): Promise<StylePreset> {
        return apiFetch(API_ENDPOINTS.styles.get(id));
    },
};

/**
 * Default presets to use when API is unavailable
 */
function getDefaultPresets(): StylePreset[] {
    return [
        { id: 'modern_minimal', name: 'Modern Minimal', description: 'Clean lines and spacious layouts', category: 'minimal', colors: ['#1a1a2e', '#ffffff', '#8b5cf6'], isPremium: false },
        { id: 'corporate_classic', name: 'Corporate Classic', description: 'Timeless business design', category: 'business', colors: ['#1e3a5f', '#ffffff', '#2563eb'], isPremium: false },
        { id: 'tech_startup', name: 'Tech Startup', description: 'Bold and modern for pitches', category: 'technology', colors: ['#0f172a', '#8b5cf6', '#06b6d4'], isPremium: false },
    ];
}

export default presentationsApi;
