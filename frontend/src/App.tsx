import { useState, useEffect, useCallback } from 'react'
import { BrowserRouter, Routes, Route, useNavigate, useParams } from 'react-router-dom'
import {
    Plus,
    Search,
    Grid3X3,
    List,
    ChevronDown,
    Folder,
    Layout,
    Lightbulb,
    Palette,
    Type,
    Trash2,
    Star,
    Clock,
    User,
    Sparkles,
    Download,
    ArrowLeft,
    Edit,
    Info
} from 'lucide-react'
import './App.css'
import { BlockEditor } from './components/BlockEditor'
import { TemplateLibrary } from './components/Templates'
import type { Template } from './components/Templates'
import { presentationsApi, type Presentation, type CreatePresentationResponse } from './services/presentationsApi'
import { API_BASE_URL } from './config/api'

type TabType = 'all' | 'recent' | 'created' | 'favorites';

// Toast notification component
interface ToastProps {
    message: string;
    type: 'info' | 'success' | 'error';
    onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({ message, type, onClose }) => {
    useEffect(() => {
        const timer = setTimeout(onClose, 3000);
        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div className={`toast toast-${type}`}>
            <Info size={16} />
            {message}
        </div>
    );
};

// Dashboard Component
const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const [presentations, setPresentations] = useState<Presentation[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<TabType>('all');
    const [viewType, setViewType] = useState<'grid' | 'list'>('grid');
    const [searchQuery, setSearchQuery] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [newTopic, setNewTopic] = useState('');
    const [numSlides, setNumSlides] = useState(5);
    const [selectedStyle, setSelectedStyle] = useState('modern_minimal');
    const [toast, setToast] = useState<{ message: string; type: 'info' | 'success' | 'error' } | null>(null);

    // Fetch presentations on mount
    useEffect(() => {
        const fetchPresentations = async () => {
            setIsLoading(true);
            try {
                const data = await presentationsApi.list();
                setPresentations(data);
            } catch (error) {
                console.error('Failed to fetch presentations:', error);
                setToast({ message: 'Could not load presentations. Backend may be offline.', type: 'error' });
            }
            setIsLoading(false);
        };

        fetchPresentations();
    }, []);

    // Filter presentations based on search AND active tab
    const filteredPresentations = presentations.filter(p => {
        // Search filter
        const matchesSearch = p.title.toLowerCase().includes(searchQuery.toLowerCase());

        // Tab filter
        let matchesTab = true;
        switch (activeTab) {
            case 'all':
                matchesTab = true;
                break;
            case 'recent':
                // Show items viewed/modified in last 7 days
                const recentDate = new Date();
                recentDate.setDate(recentDate.getDate() - 7);
                matchesTab = new Date(p.updatedAt || p.createdAt) >= recentDate;
                break;
            case 'created':
                matchesTab = p.author === 'you';
                break;
            case 'favorites':
                matchesTab = p.isFavorite === true;
                break;
        }

        return matchesSearch && matchesTab;
    });

    const handleCreateNew = async () => {
        if (!newTopic.trim()) return;

        setIsGenerating(true);
        try {
            const result: CreatePresentationResponse = await presentationsApi.generate({
                topic: newTopic,
                num_slides: numSlides,
                style_id: selectedStyle,
            });

            if (result.success) {
                // Add to presentations list
                const newPres: Presentation = {
                    id: result.presentation_id,
                    title: newTopic,
                    thumbnail: '✨',
                    createdAt: new Date().toISOString(),
                    isPrivate: true,
                    author: 'you',
                    isFavorite: false,
                    slideCount: result.slide_count,
                };
                setPresentations(prev => [newPres, ...prev]);
                setShowCreateModal(false);
                setNewTopic('');
                setToast({ message: 'Presentation generated successfully!', type: 'success' });

                // Download the file
                if (result.download_url) {
                    window.open(`${API_BASE_URL}${result.download_url}`, '_blank');
                }
            }
        } catch (error) {
            console.error('Generation failed:', error);
            setToast({ message: 'Generation failed. Please try again.', type: 'error' });
        }
        setIsGenerating(false);
    };

    const handleToggleFavorite = async (id: string, currentFavorite: boolean) => {
        try {
            await presentationsApi.toggleFavorite(id, !currentFavorite);
            setPresentations(prev =>
                prev.map(p => p.id === id ? { ...p, isFavorite: !currentFavorite } : p)
            );
        } catch (error) {
            console.error('Failed to toggle favorite:', error);
            // Optimistically update UI even if API fails
            setPresentations(prev =>
                prev.map(p => p.id === id ? { ...p, isFavorite: !currentFavorite } : p)
            );
        }
    };

    const handleEditPresentation = (presId: string) => {
        navigate(`/editor/${presId}`);
    };

    const showComingSoon = (feature: string) => {
        setToast({ message: `${feature} - Coming Soon!`, type: 'info' });
    };

    return (
        <div className="app">
            {/* Toast Notification */}
            {toast && (
                <Toast
                    message={toast.message}
                    type={toast.type}
                    onClose={() => setToast(null)}
                />
            )}

            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="logo">
                        <div className="logo-icon">
                            <Sparkles size={20} />
                        </div>
                    </div>
                </div>

                <div className="sidebar-user">
                    <div className="user-avatar">
                        <User size={24} />
                    </div>
                    <span className="user-badge">AI</span>
                </div>

                <div className="sidebar-section">
                    <div className="folder-item" onClick={() => showComingSoon('Folders')}>
                        <Folder size={18} />
                        <div className="folder-info">
                            <span className="folder-title">Folders</span>
                            <span className="folder-desc">Organize your files by topic and share them with your team.</span>
                        </div>
                        <Plus size={16} className="folder-add" />
                    </div>
                </div>

                <nav className="sidebar-nav">
                    <button className="nav-item" onClick={() => navigate('/templates')}>
                        <Layout size={18} />
                        Templates
                    </button>
                    <button className="nav-item disabled" onClick={() => showComingSoon('Inspiration')}>
                        <Lightbulb size={18} />
                        Inspiration
                    </button>
                    <button className="nav-item disabled" onClick={() => showComingSoon('Themes')}>
                        <Palette size={18} />
                        Themes
                    </button>
                    <button className="nav-item disabled" onClick={() => showComingSoon('Custom Fonts')}>
                        <Type size={18} />
                        Custom fonts
                    </button>
                    <button className="nav-item disabled" onClick={() => showComingSoon('Trash')}>
                        <Trash2 size={18} />
                        Trash
                    </button>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="main">
                {/* Header */}
                <header className="header">
                    <div className="search-box">
                        <Search size={18} />
                        <input
                            type="text"
                            placeholder="Type to search or press /"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>

                    <div className="header-actions">
                        <span className="credits">✦ Get unlimited AI</span>
                        <span className="credits">◎ 400 credits</span>
                    </div>
                </header>

                {/* Toolbar */}
                <div className="toolbar">
                    <div className="toolbar-left">
                        <h1 className="page-title">
                            <Sparkles size={20} />
                            Presentations
                        </h1>

                        <div className="toolbar-buttons">
                            <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
                                <Plus size={16} />
                                Create new
                                <span className="ai-badge">AI</span>
                            </button>
                            <button className="btn btn-secondary" onClick={() => showComingSoon('New from blank')}>
                                <Plus size={16} />
                                New from blank
                                <ChevronDown size={14} />
                            </button>
                            <button className="btn btn-secondary" onClick={() => showComingSoon('Import')}>
                                <Download size={16} />
                                Import
                                <ChevronDown size={14} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="tabs-bar">
                    <div className="tabs">
                        <button
                            className={`tab ${activeTab === 'all' ? 'active' : ''}`}
                            onClick={() => setActiveTab('all')}
                        >
                            All
                        </button>
                        <button
                            className={`tab ${activeTab === 'recent' ? 'active' : ''}`}
                            onClick={() => setActiveTab('recent')}
                        >
                            <Clock size={14} />
                            Recently viewed
                        </button>
                        <button
                            className={`tab ${activeTab === 'created' ? 'active' : ''}`}
                            onClick={() => setActiveTab('created')}
                        >
                            <User size={14} />
                            Created by you
                        </button>
                        <button
                            className={`tab ${activeTab === 'favorites' ? 'active' : ''}`}
                            onClick={() => setActiveTab('favorites')}
                        >
                            <Star size={14} />
                            Favorites
                        </button>
                    </div>

                    <div className="view-toggle">
                        <button
                            className={`view-btn ${viewType === 'grid' ? 'active' : ''}`}
                            onClick={() => setViewType('grid')}
                        >
                            <Grid3X3 size={16} />
                            Grid
                        </button>
                        <button
                            className={`view-btn ${viewType === 'list' ? 'active' : ''}`}
                            onClick={() => setViewType('list')}
                        >
                            <List size={16} />
                            List
                        </button>
                    </div>
                </div>

                {/* Loading State */}
                {isLoading ? (
                    <div className="loading-state">
                        <Sparkles size={32} className="spin" />
                        <p>Loading presentations...</p>
                    </div>
                ) : (
                    <>
                        {/* Empty State */}
                        {filteredPresentations.length === 0 ? (
                            <div className="empty-state">
                                <Sparkles size={48} />
                                <h3>
                                    {presentations.length === 0
                                        ? 'No presentations yet'
                                        : 'No presentations match your filters'}
                                </h3>
                                <p>
                                    {presentations.length === 0
                                        ? 'Create your first AI-powered presentation!'
                                        : 'Try adjusting your search or filters'}
                                </p>
                                {presentations.length === 0 && (
                                    <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
                                        <Plus size={16} />
                                        Create presentation
                                    </button>
                                )}
                            </div>
                        ) : (
                            /* Presentations Grid */
                            <div className={`presentations-grid ${viewType}`}>
                                {filteredPresentations.map((pres) => (
                                    <div key={pres.id} className="presentation-card card">
                                        <div className="card-thumbnail">
                                            <span className="thumbnail-emoji">{pres.thumbnail}</span>
                                            <button
                                                className={`card-favorite-btn ${pres.isFavorite ? 'active' : ''}`}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleToggleFavorite(pres.id, pres.isFavorite);
                                                }}
                                                title={pres.isFavorite ? 'Remove from favorites' : 'Add to favorites'}
                                            >
                                                <Star size={16} fill={pres.isFavorite ? 'currentColor' : 'none'} />
                                            </button>
                                            <button
                                                className="card-edit-btn"
                                                onClick={() => handleEditPresentation(pres.id)}
                                                title="Edit presentation"
                                            >
                                                <Edit size={16} />
                                            </button>
                                        </div>
                                        <div className="card-content">
                                            <h3 className="card-title">{pres.title}</h3>
                                            <div className="card-meta">
                                                <span className={`badge ${pres.isPrivate ? 'badge-private' : 'badge-public'}`}>
                                                    {pres.isPrivate ? '🔒 Private' : '🌐 Public'}
                                                </span>
                                            </div>
                                            <div className="card-footer">
                                                <span className="author">👤 Created by {pres.author}</span>
                                                <span className="date">Last viewed {pres.createdAt}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                )}
            </main>

            {/* Create Modal */}
            {showCreateModal && (
                <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Create New Presentation</h2>

                        <div className="form-group">
                            <label>What's your presentation about?</label>
                            <textarea
                                value={newTopic}
                                onChange={(e) => setNewTopic(e.target.value)}
                                placeholder="e.g., The Future of AI in Healthcare"
                                rows={3}
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Number of slides</label>
                                <input
                                    type="number"
                                    min={3}
                                    max={30}
                                    value={numSlides}
                                    onChange={(e) => setNumSlides(parseInt(e.target.value) || 5)}
                                />
                            </div>
                            <div className="form-group">
                                <label>Style</label>
                                <select value={selectedStyle} onChange={(e) => setSelectedStyle(e.target.value)}>
                                    <option value="modern_minimal">Modern Minimal</option>
                                    <option value="corporate_classic">Corporate Classic</option>
                                    <option value="tech_startup">Tech Startup</option>
                                    <option value="dark_cyber">Dark Cyber</option>
                                    <option value="creative_bold">Creative Bold</option>
                                    <option value="nature_organic">Nature Organic</option>
                                </select>
                            </div>
                        </div>

                        <div className="modal-actions">
                            <button className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                                Cancel
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={handleCreateNew}
                                disabled={isGenerating || !newTopic.trim()}
                            >
                                {isGenerating ? 'Generating...' : 'Generate with AI'}
                                <Sparkles size={16} />
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// Editor Page Component
const EditorPage: React.FC = () => {
    const navigate = useNavigate();
    const { id } = useParams<{ id: string }>();

    const handleSave = useCallback(() => {
        console.log('Saving presentation:', id);
        navigate('/');
    }, [id, navigate]);

    return (
        <div className="app app-editor">
            <div className="editor-top-bar">
                <button className="btn btn-secondary" onClick={() => navigate('/')}>
                    <ArrowLeft size={16} />
                    Back to Dashboard
                </button>
                <span className="editor-title">Editing: {id || 'New Presentation'}</span>
            </div>
            <BlockEditor
                onSave={handleSave}
                onPreview={() => console.log('Preview mode')}
            />
        </div>
    );
};

// Templates Page Component
const TemplatesPage: React.FC = () => {
    const navigate = useNavigate();

    const handleTemplateSelect = (template: Template) => {
        // Navigate to dashboard with template pre-selected
        navigate('/', { state: { selectedStyle: template.styleId, openModal: true } });
    };

    return (
        <div className="app">
            <div className="editor-top-bar">
                <button className="btn btn-secondary" onClick={() => navigate('/')}>
                    <ArrowLeft size={16} />
                    Back to Dashboard
                </button>
            </div>
            <TemplateLibrary onSelect={handleTemplateSelect} />
        </div>
    );
};

// Main App with Router
function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/editor" element={<EditorPage />} />
                <Route path="/editor/:id" element={<EditorPage />} />
                <Route path="/templates" element={<TemplatesPage />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App
