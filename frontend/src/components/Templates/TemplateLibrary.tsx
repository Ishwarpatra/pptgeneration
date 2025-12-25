import React, { useState, useMemo } from 'react';
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
    Check
} from 'lucide-react';
import type { Template, TemplateCategory } from './types';
import './TemplateLibrary.css';

interface TemplateLibraryProps {
    onSelect?: (template: Template) => void;
}

// Predefined templates
const TEMPLATES: Template[] = [
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
    {
        id: 'academic_focus',
        name: 'Academic Focus',
        description: 'Structured layouts perfect for educational content',
        thumbnail: '📚',
        category: 'education',
        styleId: 'academic_focus',
        slideCount: 16,
        isPremium: false,
        colors: ['#fefce8', '#eab308', '#1e3a8a']
    },
    {
        id: 'pitch_deck_pro',
        name: 'Pitch Deck Pro',
        description: 'Investor-ready design with compelling data visualization',
        thumbnail: '💼',
        category: 'business',
        styleId: 'pitch_deck_pro',
        slideCount: 18,
        isPremium: true,
        colors: ['#18181b', '#fafafa', '#a855f7']
    },
    {
        id: 'marketing_splash',
        name: 'Marketing Splash',
        description: 'Eye-catching layouts for marketing campaigns',
        thumbnail: '📢',
        category: 'marketing',
        styleId: 'marketing_splash',
        slideCount: 12,
        isPremium: false,
        colors: ['#fff1f2', '#fb7185', '#be123c']
    },
    {
        id: 'gradient_dreams',
        name: 'Gradient Dreams',
        description: 'Smooth color transitions and modern aesthetics',
        thumbnail: '🌈',
        category: 'creative',
        styleId: 'gradient_dreams',
        slideCount: 10,
        isPremium: true,
        colors: ['#4f46e5', '#7c3aed', '#ec4899']
    },
    {
        id: 'mono_elegance',
        name: 'Mono Elegance',
        description: 'Sophisticated black and white with accent colors',
        thumbnail: '⚫',
        category: 'minimal',
        styleId: 'mono_elegance',
        slideCount: 12,
        isPremium: false,
        colors: ['#000000', '#ffffff', '#737373']
    },
    {
        id: 'edu_playful',
        name: 'Educational Playful',
        description: 'Fun and engaging design for interactive learning',
        thumbnail: '🎓',
        category: 'education',
        styleId: 'edu_playful',
        slideCount: 14,
        isPremium: false,
        colors: ['#fef9c3', '#facc15', '#4f46e5']
    }
];

const CATEGORIES: { id: TemplateCategory | 'all'; label: string; icon: React.ReactNode }[] = [
    { id: 'all', label: 'All Templates', icon: <Sparkles size={16} /> },
    { id: 'business', label: 'Business', icon: <Building2 size={16} /> },
    { id: 'education', label: 'Education', icon: <GraduationCap size={16} /> },
    { id: 'creative', label: 'Creative', icon: <Palette size={16} /> },
    { id: 'technology', label: 'Technology', icon: <Cpu size={16} /> },
    { id: 'minimal', label: 'Minimal', icon: <Minimize2 size={16} /> },
    { id: 'marketing', label: 'Marketing', icon: <Megaphone size={16} /> },
];

export const TemplateLibrary: React.FC<TemplateLibraryProps> = ({
    onSelect
}) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [activeCategory, setActiveCategory] = useState<TemplateCategory | 'all'>('all');
    const [showPremiumOnly, setShowPremiumOnly] = useState(false);

    const filteredTemplates = useMemo(() => {
        return TEMPLATES.filter(template => {
            const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                template.description.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesCategory = activeCategory === 'all' || template.category === activeCategory;
            const matchesPremium = !showPremiumOnly || template.isPremium;

            return matchesSearch && matchesCategory && matchesPremium;
        });
    }, [searchQuery, activeCategory, showPremiumOnly]);

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
        </div>
    );
};

export default TemplateLibrary;
