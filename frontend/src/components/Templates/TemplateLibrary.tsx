import React, { useState, useMemo, useEffect } from 'react';
import {
    Search,
    Sparkles,
    Building2,
    GraduationCap,
    Palette,
    Cpu,
    Minimize2,
    Megaphone,
    Crown,
    Check,
    Loader2
} from 'lucide-react';
import type { Template, TemplateCategory } from './types';
import { stylesApi, type StylePreset } from '../../services/presentationsApi';
import './TemplateLibrary.css';

interface TemplateLibraryProps {
    onSelect?: (template: Template) => void;
}

// Default templates for fallback when API is unavailable
const DEFAULT_TEMPLATES: Template[] = [
    {
        id: 'modern_minimal',
        name: 'Modern Minimal',
        description: 'Clean lines and spacious layouts for professional presentations',
        thumbnail: '◻️',
        category: 'minimal',
        styleId: 'modern_minimal',
        slideCount: 12,
        isPremium: false,
        colors: ['#1a1a2e', '#ffffff', '#8b5cf6']
    },
    {
        id: 'corporate_classic',
        name: 'Corporate Classic',
        description: 'Timeless design for business meetings and reports',
        thumbnail: '📊',
        category: 'business',
        styleId: 'corporate_classic',
        slideCount: 15,
        isPremium: false,
        colors: ['#1e3a5f', '#ffffff', '#2563eb']
    },
    {
        id: 'tech_startup',
        name: 'Tech Startup',
        description: 'Bold gradients and modern typography for innovative pitches',
        thumbnail: '🚀',
        category: 'technology',
        styleId: 'tech_startup',
        slideCount: 10,
        isPremium: false,
        colors: ['#0f172a', '#8b5cf6', '#06b6d4']
    },
    {
        id: 'dark_cyber',
        name: 'Dark Cyber',
        description: 'Futuristic neon aesthetics for tech presentations',
        thumbnail: '🌐',
        category: 'technology',
        styleId: 'dark_cyber',
        slideCount: 12,
        isPremium: true,
        colors: ['#0a0a0f', '#00ff88', '#00d4ff']
    },
    {
        id: 'creative_bold',
        name: 'Creative Bold',
        description: 'Vibrant colors and expressive layouts for creative work',
        thumbnail: '🎨',
        category: 'creative',
        styleId: 'creative_bold',
        slideCount: 14,
        isPremium: true,
        colors: ['#fef3c7', '#f97316', '#ec4899']
    },
    {
        id: 'nature_organic',
        name: 'Nature Organic',
        description: 'Earthy tones and flowing designs inspired by nature',
        thumbnail: '🌿',
        category: 'creative',
        styleId: 'nature_organic',
        slideCount: 10,
        isPremium: false,
        colors: ['#f0fdf4', '#22c55e', '#166534']
    },
];

const CATEGORY_THUMBNAILS: Record<string, string> = {
    'minimal': '◻️',
    'business': '📊',
    'technology': '🚀',
    'creative': '🎨',
    'education': '📚',
    'marketing': '📢',
};

const CATEGORIES: { id: TemplateCategory | 'all'; label: string; icon: React.ReactNode }[] = [
    { id: 'all', label: 'All Templates', icon: <Sparkles size={16} /> },
    { id: 'business', label: 'Business', icon: <Building2 size={16} /> },
    { id: 'education', label: 'Education', icon: <GraduationCap size={16} /> },
    { id: 'creative', label: 'Creative', icon: <Palette size={16} /> },
    { id: 'technology', label: 'Technology', icon: <Cpu size={16} /> },
    { id: 'minimal', label: 'Minimal', icon: <Minimize2 size={16} /> },
    { id: 'marketing', label: 'Marketing', icon: <Megaphone size={16} /> },
];

/**
 * Convert StylePreset from API to Template format
 */
function presetToTemplate(preset: StylePreset): Template {
    return {
        id: preset.id,
        name: preset.name,
        description: preset.description,
        thumbnail: preset.thumbnail || CATEGORY_THUMBNAILS[preset.category] || '✨',
        category: preset.category as TemplateCategory,
        styleId: preset.id,
        slideCount: preset.slideCount || 10,
        isPremium: preset.isPremium,
        colors: preset.colors,
    };
}

export const TemplateLibrary: React.FC<TemplateLibraryProps> = ({
    onSelect
}) => {
    const [templates, setTemplates] = useState<Template[]>(DEFAULT_TEMPLATES);
    const [isLoading, setIsLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeCategory, setActiveCategory] = useState<TemplateCategory | 'all'>('all');
    const [showPremiumOnly, setShowPremiumOnly] = useState(false);

    // Fetch templates from API on mount
    useEffect(() => {
        const fetchTemplates = async () => {
            setIsLoading(true);
            try {
                const presets = await stylesApi.getPresets();
                if (presets.length > 0) {
                    setTemplates(presets.map(presetToTemplate));
                }
                // If empty, keep default templates
            } catch (error) {
                console.error('Failed to fetch templates, using defaults:', error);
                // Keep default templates on error
            }
            setIsLoading(false);
        };

        fetchTemplates();
    }, []);

    const filteredTemplates = useMemo(() => {
        return templates.filter(template => {
            const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                template.description.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesCategory = activeCategory === 'all' || template.category === activeCategory;
            const matchesPremium = !showPremiumOnly || template.isPremium;

            return matchesSearch && matchesCategory && matchesPremium;
        });
    }, [templates, searchQuery, activeCategory, showPremiumOnly]);

    return (
        <div className="template-library">
            {/* Header */}
            <div className="library-header">
                <div className="header-content">
                    <h2>
                        <Sparkles size={24} />
                        Template Gallery
                    </h2>
                    <p>Choose a template to get started or customize your own</p>
                </div>

                <div className="header-actions">
                    <div className="search-box">
                        <Search size={18} />
                        <input
                            type="text"
                            placeholder="Search templates..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>

                    <button
                        className={`premium-toggle ${showPremiumOnly ? 'active' : ''}`}
                        onClick={() => setShowPremiumOnly(!showPremiumOnly)}
                    >
                        <Crown size={16} />
                        Premium
                    </button>
                </div>
            </div>

            {/* Categories */}
            <div className="category-tabs">
                {CATEGORIES.map(category => (
                    <button
                        key={category.id}
                        className={`category-tab ${activeCategory === category.id ? 'active' : ''}`}
                        onClick={() => setActiveCategory(category.id)}
                    >
                        {category.icon}
                        <span>{category.label}</span>
                    </button>
                ))}
            </div>

            {/* Loading State */}
            {isLoading ? (
                <div className="loading-state">
                    <Loader2 size={32} className="spin" />
                    <p>Loading templates...</p>
                </div>
            ) : (
                <>
                    {/* Template Grid */}
                    <div className="template-grid">
                        {filteredTemplates.map(template => (
                            <div
                                key={template.id}
                                className="template-card"
                                onClick={() => onSelect?.(template)}
                            >
                                {template.isPremium && (
                                    <div className="premium-badge">
                                        <Crown size={12} />
                                        PRO
                                    </div>
                                )}

                                <div
                                    className="template-preview"
                                    style={{
                                        background: `linear-gradient(135deg, ${template.colors[0]} 0%, ${template.colors[1]} 50%, ${template.colors[2]} 100%)`
                                    }}
                                >
                                    <span className="preview-emoji">{template.thumbnail}</span>
                                </div>

                                <div className="template-info">
                                    <h3>{template.name}</h3>
                                    <p>{template.description}</p>

                                    <div className="template-meta">
                                        <span className="slide-count">{template.slideCount} slides</span>
                                        <div className="color-dots">
                                            {template.colors.map((color, i) => (
                                                <span
                                                    key={i}
                                                    className="color-dot"
                                                    style={{ background: color }}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                <button className="use-template-btn">
                                    <Check size={16} />
                                    Use Template
                                </button>
                            </div>
                        ))}
                    </div>

                    {filteredTemplates.length === 0 && (
                        <div className="no-results">
                            <Sparkles size={48} />
                            <h3>No templates found</h3>
                            <p>Try adjusting your search or filters</p>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default TemplateLibrary;
