import { useState } from 'react'
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
    Edit
} from 'lucide-react'
import './App.css'
import { BlockEditor } from './components/BlockEditor'
import { TemplateLibrary } from './components/Templates'
import type { Template } from './components/Templates'

type AppView = 'dashboard' | 'editor' | 'templates';

interface Presentation {
    id: string
    title: string
    thumbnail: string
    createdAt: string
    isPrivate: boolean
    author: string
}

// Mock data for presentations
const MOCK_PRESENTATIONS: Presentation[] = [
    { id: '1', title: 'EYRA: Accessible Education for the Visually...', thumbnail: '🎓', createdAt: '2 months ago', isPrivate: true, author: 'you' },
    { id: '2', title: 'Smart Inventory Solutions', thumbnail: '📦', createdAt: '4 months ago', isPrivate: false, author: 'you' },
    { id: '3', title: 'AR/VR in Education: Immersive Learning...', thumbnail: '🥽', createdAt: '7 months ago', isPrivate: true, author: 'you' },
    { id: '4', title: 'A Balanced Approach to Packaging: Innovation...', thumbnail: '📊', createdAt: '7 months ago', isPrivate: true, author: 'you' },
    { id: '5', title: 'The Immersive Revolution: AR and VR in Learning', thumbnail: '🌐', createdAt: '7 months ago', isPrivate: true, author: 'you' },
    { id: '6', title: 'Why Hurry and Worry?', thumbnail: '🧘', createdAt: '2 years ago', isPrivate: true, author: 'you' },
    { id: '7', title: 'Mastering the Basics: A Quiz on AI for Beginners', thumbnail: '🤖', createdAt: '2 years ago', isPrivate: true, author: 'you' },
    { id: '8', title: 'Quiz on AI', thumbnail: '❓', createdAt: '2 years ago', isPrivate: true, author: 'you' },
]

function App() {
    const [presentations, setPresentations] = useState<Presentation[]>(MOCK_PRESENTATIONS)
    const [activeTab, setActiveTab] = useState('all')
    const [viewType, setViewType] = useState<'grid' | 'list'>('grid')
    const [searchQuery, setSearchQuery] = useState('')
    const [showCreateModal, setShowCreateModal] = useState(false)
    const [isGenerating, setIsGenerating] = useState(false)
    const [newTopic, setNewTopic] = useState('')
    const [numSlides, setNumSlides] = useState(5)
    const [selectedStyle, setSelectedStyle] = useState('modern_minimal')
    const [currentView, setCurrentView] = useState<AppView>('dashboard')
    const [editingPresentationId, setEditingPresentationId] = useState<string | null>(null)

    const filteredPresentations = presentations.filter(p =>
        p.title.toLowerCase().includes(searchQuery.toLowerCase())
    )

    const handleCreateNew = async () => {
        if (!newTopic.trim()) return

        setIsGenerating(true)
        try {
            const response = await fetch('http://localhost:8000/api/generate/presentation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: newTopic,
                    num_slides: numSlides,
                    style_id: selectedStyle,
                }),
            })

            const data = await response.json()

            if (data.success) {
                // Add to presentations list
                const newPres: Presentation = {
                    id: Date.now().toString(),
                    title: newTopic,
                    thumbnail: '✨',
                    createdAt: 'Just now',
                    isPrivate: true,
                    author: 'you',
                }
                setPresentations([newPres, ...presentations])
                setShowCreateModal(false)
                setNewTopic('')

                // Download the file
                if (data.download_url) {
                    window.open(`http://localhost:8000${data.download_url}`, '_blank')
                }
            }
        } catch (error) {
            console.error('Generation failed:', error)
        }
        setIsGenerating(false)
    }

    const handleTemplateSelect = (template: Template) => {
        setSelectedStyle(template.styleId)
        setCurrentView('dashboard')
        setShowCreateModal(true)
    }

    const handleEditPresentation = (presId: string) => {
        setEditingPresentationId(presId)
        setCurrentView('editor')
    }

    const handleEditorSave = () => {
        console.log('Saving presentation...')
        setCurrentView('dashboard')
        setEditingPresentationId(null)
    }

    // Render different views based on currentView state
    if (currentView === 'editor') {
        return (
            <div className="app app-editor">
                <div className="editor-top-bar">
                    <button className="btn btn-secondary" onClick={() => setCurrentView('dashboard')}>
                        <ArrowLeft size={16} />
                        Back to Dashboard
                    </button>
                </div>
                <BlockEditor
                    onSave={handleEditorSave}
                    onPreview={() => console.log('Preview mode')}
                />
            </div>
        )
    }

    if (currentView === 'templates') {
        return (
            <div className="app">
                <div className="editor-top-bar">
                    <button className="btn btn-secondary" onClick={() => setCurrentView('dashboard')}>
                        <ArrowLeft size={16} />
                        Back to Dashboard
                    </button>
                </div>
                <TemplateLibrary onSelect={handleTemplateSelect} />
            </div>
        )
    }

    // Default: Dashboard view

    return (
        <div className="app">
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
                    <div className="folder-item">
                        <Folder size={18} />
                        <div className="folder-info">
                            <span className="folder-title">Folders</span>
                            <span className="folder-desc">Organize your files by topic and share them with your team.</span>
                        </div>
                        <Plus size={16} className="folder-add" />
                    </div>
                </div>

                <nav className="sidebar-nav">
                    <button className="nav-item" onClick={() => setCurrentView('templates')}>
                        <Layout size={18} />
                        Templates
                    </button>
                    <button className="nav-item">
                        <Lightbulb size={18} />
                        Inspiration
                    </button>
                    <button className="nav-item">
                        <Palette size={18} />
                        Themes
                    </button>
                    <button className="nav-item">
                        <Type size={18} />
                        Custom fonts
                    </button>
                    <button className="nav-item">
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
                            Gammas
                        </h1>

                        <div className="toolbar-buttons">
                            <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
                                <Plus size={16} />
                                Create new
                                <span className="ai-badge">AI</span>
                            </button>
                            <button className="btn btn-secondary">
                                <Plus size={16} />
                                New from blank
                                <ChevronDown size={14} />
                            </button>
                            <button className="btn btn-secondary">
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

                {/* Presentations Grid */}
                <div className={`presentations-grid ${viewType}`}>
                    {filteredPresentations.map((pres) => (
                        <div key={pres.id} className="presentation-card card">
                            <div className="card-thumbnail">
                                <span className="thumbnail-emoji">{pres.thumbnail}</span>
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
    )
}

export default App
