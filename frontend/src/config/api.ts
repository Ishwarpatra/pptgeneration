/**
 * API Configuration
 * 
 * Centralized configuration for all API endpoints.
 * Uses Vite environment variables for flexibility across environments.
 */

// Get API base URL from environment variables with fallback
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * API endpoints configuration
 */
export const API_ENDPOINTS = {
    // Presentation endpoints
    presentations: {
        list: `${API_BASE_URL}/api/presentations`,
        get: (id: string) => `${API_BASE_URL}/api/presentations/${id}`,
        create: `${API_BASE_URL}/api/presentations`,
        update: (id: string) => `${API_BASE_URL}/api/presentations/${id}`,
        delete: (id: string) => `${API_BASE_URL}/api/presentations/${id}`,
        generate: `${API_BASE_URL}/api/generate/presentation`,
        download: (id: string) => `${API_BASE_URL}/api/presentations/${id}/download`,
    },

    // Style/Template endpoints
    styles: {
        presets: `${API_BASE_URL}/api/style/presets`,
        get: (id: string) => `${API_BASE_URL}/api/style/presets/${id}`,
        mix: `${API_BASE_URL}/api/style/mix`,
    },

    // Visual synthesis endpoints
    visual: {
        styles: `${API_BASE_URL}/api/visual/styles`,
        generate: `${API_BASE_URL}/api/visual/generate`,
        suggest: `${API_BASE_URL}/api/visual/suggest`,
        image: (filename: string) => `${API_BASE_URL}/api/visual/image/${filename}`,
        provider: `${API_BASE_URL}/api/visual/provider`,
    },

    // Reference analysis
    reference: {
        analyze: `${API_BASE_URL}/api/reference/analyze`,
        extract: `${API_BASE_URL}/api/reference/extract-style`,
    },

    // Health check
    health: `${API_BASE_URL}/health`,
} as const;

/**
 * Generic fetch wrapper with error handling
 */
export async function apiFetch<T>(
    url: string,
    options: RequestInit = {}
): Promise<T> {
    const response = await fetch(url, {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    });

    if (!response.ok) {
        let errorMessage = `HTTP error ${response.status}`;
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
            // Response wasn't JSON
        }
        throw new Error(errorMessage);
    }

    return response.json();
}

export default API_ENDPOINTS;
