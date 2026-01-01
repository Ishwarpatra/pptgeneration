import React, { useState, useEffect } from 'react';
import {
    Sparkles,
    Image,
    Wand2,
    Loader2,
    X,
    Check,
    RefreshCw,
    Palette
} from 'lucide-react';
import { visualApi, type ImageStyle } from './visualApi';
import type { ImageSuggestion } from './visualApi';
import './ImageGenerator.css';

interface ImageGeneratorProps {
    slideTitle: string;
    slideContent: string;
    onImageGenerated: (imageUrl: string) => void;
    onClose: () => void;
}

// Default styles to use when API is unavailable
const DEFAULT_IMAGE_STYLES: { id: string; name: string; emoji: string }[] = [
    { id: 'corporate', name: 'Corporate', emoji: '💼' },
    { id: 'photorealistic', name: 'Photo', emoji: '📷' },
    { id: 'illustration', name: 'Illustration', emoji: '🎨' },
    { id: 'flat_design', name: 'Flat', emoji: '◻️' },
    { id: 'isometric', name: 'Isometric', emoji: '🔷' },
    { id: 'minimalist', name: 'Minimal', emoji: '⚪' },
    { id: 'abstract', name: 'Abstract', emoji: '🌀' },
    { id: 'infographic', name: 'Infographic', emoji: '📊' },
];

export const ImageGenerator: React.FC<ImageGeneratorProps> = ({
    slideTitle,
    slideContent,
    onImageGenerated,
    onClose
}) => {
    const [prompt, setPrompt] = useState('');
    const [selectedStyle, setSelectedStyle] = useState('corporate');
    const [isGenerating, setIsGenerating] = useState(false);
    const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
    const [isLoadingStyles, setIsLoadingStyles] = useState(true);
    const [suggestions, setSuggestions] = useState<ImageSuggestion[]>([]);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [providerInfo, setProviderInfo] = useState<string>('');
    const [imageStyles, setImageStyles] = useState(DEFAULT_IMAGE_STYLES);

    // Load styles and suggestions on mount
    useEffect(() => {
        loadStyles();
        loadSuggestions();
        loadProviderInfo();
    }, [slideTitle, slideContent]);

    const loadStyles = async () => {
        setIsLoadingStyles(true);
        try {
            const response = await visualApi.getStyles();
            if (response.styles && response.styles.length > 0) {
                // Convert API styles to our format
                const fetchedStyles = response.styles.map((s: ImageStyle) => ({
                    id: s.id,
                    name: s.name,
                    emoji: getStyleEmoji(s.id),
                }));
                setImageStyles(fetchedStyles);
            }
            // If empty, keep defaults
        } catch (err) {
            console.error('Failed to load styles, using defaults:', err);
            // Keep default styles on error
        }
        setIsLoadingStyles(false);
    };

    const loadSuggestions = async () => {
        if (!slideTitle && !slideContent) return;

        setIsLoadingSuggestions(true);
        try {
            const analysis = await visualApi.suggestImages(slideTitle, slideContent);
            setSuggestions(analysis.suggestions);

            // Auto-fill first suggestion as prompt
            if (analysis.suggestions.length > 0) {
                setPrompt(analysis.suggestions[0].suggested_prompt);
                setSelectedStyle(analysis.suggestions[0].style);
            }
        } catch (err) {
            console.error('Failed to load suggestions:', err);
        }
        setIsLoadingSuggestions(false);
    };

    const loadProviderInfo = async () => {
        try {
            const info = await visualApi.getProviderInfo();
            setProviderInfo(info.details.name || info.current_provider);
        } catch (err) {
            setProviderInfo('AI Provider');
        }
    };

    const handleGenerate = async () => {
        if (!prompt.trim()) return;

        setIsGenerating(true);
        setError(null);

        try {
            const result = await visualApi.generateImage({
                prompt,
                style: selectedStyle,
                aspect_ratio: '16:9',
                slide_context: slideTitle,
                quality: 'standard'
            });

            if (result.success && result.image_path) {
                const filename = result.image_path.split(/[/\\]/).pop();
                const imageUrl = visualApi.getImageUrl(filename!);
                setGeneratedImage(imageUrl);
            } else {
                setError(result.error || 'Generation failed');
            }
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to generate image';
            setError(errorMessage);
        }

        setIsGenerating(false);
    };

    const handleUseImage = () => {
        if (generatedImage) {
            onImageGenerated(generatedImage);
            onClose();
        }
    };

    const applySuggestion = (suggestion: ImageSuggestion) => {
        setPrompt(suggestion.suggested_prompt);
        setSelectedStyle(suggestion.style);
    };

    return (
        <div className="image-generator-overlay" onClick={onClose}>
            <div className="image-generator-modal" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="ig-header">
                    <div className="ig-title">
                        <Sparkles size={20} />
                        <h3>AI Image Generator</h3>
                        <span className="provider-badge">{providerInfo}</span>
                    </div>
                    <button className="ig-close" onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                <div className="ig-content">
                    {/* Left Panel - Controls */}
                    <div className="ig-controls">
                        {/* Prompt Input */}
                        <div className="ig-section">
                            <label>
                                <Wand2 size={14} />
                                Describe your image
                            </label>
                            <textarea
                                value={prompt}
                                onChange={e => setPrompt(e.target.value)}
                                placeholder="A professional business team collaborating in a modern office..."
                                rows={4}
                            />
                        </div>

                        {/* AI Suggestions */}
                        {isLoadingSuggestions && (
                            <div className="ig-section">
                                <label>
                                    <Loader2 size={14} className="spin" />
                                    Loading suggestions...
                                </label>
                            </div>
                        )}
                        {!isLoadingSuggestions && suggestions.length > 0 && (
                            <div className="ig-section">
                                <label>
                                    <Sparkles size={14} />
                                    AI Suggestions
                                </label>
                                <div className="ig-suggestions">
                                    {suggestions.map((suggestion, i) => (
                                        <button
                                            key={i}
                                            className="suggestion-chip"
                                            onClick={() => applySuggestion(suggestion)}
                                            title={suggestion.rationale}
                                        >
                                            <span className="suggestion-confidence">
                                                {Math.round(suggestion.confidence * 100)}%
                                            </span>
                                            {suggestion.suggested_prompt.substring(0, 50)}...
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Style Selection */}
                        <div className="ig-section">
                            <label>
                                <Palette size={14} />
                                Image Style
                                {isLoadingStyles && <Loader2 size={12} className="spin" style={{ marginLeft: 8 }} />}
                            </label>
                            <div className="ig-styles">
                                {imageStyles.map(style => (
                                    <button
                                        key={style.id}
                                        className={`style-btn ${selectedStyle === style.id ? 'active' : ''}`}
                                        onClick={() => setSelectedStyle(style.id)}
                                    >
                                        <span className="style-emoji">{style.emoji}</span>
                                        <span className="style-name">{style.name}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Generate Button */}
                        <button
                            className="ig-generate-btn"
                            onClick={handleGenerate}
                            disabled={isGenerating || !prompt.trim()}
                        >
                            {isGenerating ? (
                                <>
                                    <Loader2 size={18} className="spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <Image size={18} />
                                    Generate Image
                                </>
                            )}
                        </button>

                        {error && (
                            <div className="ig-error">
                                ⚠️ {error}
                            </div>
                        )}
                    </div>

                    {/* Right Panel - Preview */}
                    <div className="ig-preview">
                        {generatedImage ? (
                            <div className="ig-result">
                                <img src={generatedImage} alt="Generated" />
                                <div className="ig-result-actions">
                                    <button
                                        className="btn-regenerate"
                                        onClick={handleGenerate}
                                        disabled={isGenerating}
                                    >
                                        <RefreshCw size={16} />
                                        Regenerate
                                    </button>
                                    <button
                                        className="btn-use"
                                        onClick={handleUseImage}
                                    >
                                        <Check size={16} />
                                        Use This Image
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="ig-placeholder">
                                <Image size={48} />
                                <p>Your generated image will appear here</p>
                                <span>16:9 Widescreen format</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

/**
 * Get emoji for style ID
 */
function getStyleEmoji(styleId: string): string {
    const emojiMap: Record<string, string> = {
        'corporate': '💼',
        'photorealistic': '📷',
        'illustration': '🎨',
        'flat_design': '◻️',
        'isometric': '🔷',
        'minimalist': '⚪',
        'abstract': '🌀',
        'infographic': '📊',
        'watercolor': '🖌️',
        'icon': '🔷',
    };
    return emojiMap[styleId] || '✨';
}

export default ImageGenerator;
