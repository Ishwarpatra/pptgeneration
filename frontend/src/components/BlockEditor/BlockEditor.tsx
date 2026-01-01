import React, { useState } from 'react';
import {
    Plus,
    Type,
    Heading1,
    List,
    Image,
    Minus,
    Quote,
    Code,
    GripVertical,
    Trash2,
    ChevronLeft,
    ChevronRight,
    Save,
    Eye,
    Sparkles
} from 'lucide-react';
import type { Block, Slide, BlockType } from './types';
import { ImageGenerator } from './ImageGenerator';
import { usePresentation, createBlock, PresentationProvider } from './PresentationContext';
import './BlockEditor.css';

interface BlockEditorProps {
    initialSlides?: Slide[];
    onSave?: (slides: Slide[]) => void;
    onPreview?: (slides: Slide[]) => void;
}

const BLOCK_TYPES: { type: BlockType; icon: React.ReactNode; label: string }[] = [
    { type: 'heading', icon: <Heading1 size={16} />, label: 'Heading' },
    { type: 'text', icon: <Type size={16} />, label: 'Text' },
    { type: 'bullet', icon: <List size={16} />, label: 'Bullet List' },
    { type: 'image', icon: <Image size={16} />, label: 'Image' },
    { type: 'quote', icon: <Quote size={16} />, label: 'Quote' },
    { type: 'code', icon: <Code size={16} />, label: 'Code' },
    { type: 'divider', icon: <Minus size={16} />, label: 'Divider' },
];

/**
 * Internal BlockEditor component that uses context.
 */
const BlockEditorInternal: React.FC<BlockEditorProps> = ({
    onSave,
    onPreview
}) => {
    const {
        state,
        currentSlide,
        addSlide,
        deleteSlide,
        goToSlide,
        nextSlide,
        prevSlide,
        addBlock,
        updateBlock,
        updateBlockMetadata,
        deleteBlock,
        reorderBlocks,
        getSlides,
    } = usePresentation();

    const { slides, currentSlideIndex } = state;

    const [showBlockMenu, setShowBlockMenu] = useState(false);
    const [draggedBlockIndex, setDraggedBlockIndex] = useState<number | null>(null);
    const [showImageGenerator, setShowImageGenerator] = useState(false);
    const [activeImageBlockId, setActiveImageBlockId] = useState<string | null>(null);

    const handleAddBlock = (type: BlockType) => {
        const newBlock = createBlock(type, type === 'divider' ? '' : 'New content...');
        addBlock(newBlock);

        // If adding an image block, open the AI generator
        if (type === 'image') {
            setActiveImageBlockId(newBlock.id);
            setShowImageGenerator(true);
        }
        setShowBlockMenu(false);
    };

    const handleImageGenerated = (imageUrl: string) => {
        if (activeImageBlockId) {
            updateBlock(activeImageBlockId, imageUrl);
            updateBlockMetadata(activeImageBlockId, { imageUrl });
        }
        setShowImageGenerator(false);
        setActiveImageBlockId(null);
    };

    const openImageGenerator = (blockId: string) => {
        setActiveImageBlockId(blockId);
        setShowImageGenerator(true);
    };

    const handleUpdateBlock = (blockId: string, content: string) => {
        updateBlock(blockId, content);
    };

    const handleDeleteBlock = (blockId: string) => {
        deleteBlock(blockId);
    };

    const handleDragStart = (index: number) => {
        setDraggedBlockIndex(index);
    };

    const handleDragOver = (e: React.DragEvent, index: number) => {
        e.preventDefault();
        if (draggedBlockIndex === null || draggedBlockIndex === index) return;

        reorderBlocks(draggedBlockIndex, index);
        setDraggedBlockIndex(index);
    };

    const handleDragEnd = () => {
        setDraggedBlockIndex(null);
    };

    const handleAddSlide = () => {
        addSlide();
    };

    const handleDeleteSlide = () => {
        deleteSlide();
    };

    const handleSave = () => {
        onSave?.(getSlides());
    };

    const handlePreview = () => {
        onPreview?.(getSlides());
    };

    const renderBlock = (block: Block, index: number) => {
        const isHeading = block.type === 'heading';
        const isBullet = block.type === 'bullet';
        const isDivider = block.type === 'divider';
        const isQuote = block.type === 'quote';
        const isCode = block.type === 'code';
        const isImage = block.type === 'image';

        return (
            <div
                key={block.id}
                className={`block-item ${block.type} ${draggedBlockIndex === index ? 'dragging' : ''}`}
                draggable
                onDragStart={() => handleDragStart(index)}
                onDragOver={(e) => handleDragOver(e, index)}
                onDragEnd={handleDragEnd}
            >
                <div className="block-handle">
                    <GripVertical size={14} />
                </div>

                <div className="block-content">
                    {isDivider ? (
                        <hr className="block-divider" />
                    ) : isImage ? (
                        <div className="block-image">
                            {block.metadata?.imageUrl ? (
                                <img src={block.metadata.imageUrl as string} alt="Slide image" />
                            ) : (
                                <button
                                    className="generate-image-btn"
                                    onClick={() => openImageGenerator(block.id)}
                                >
                                    <Sparkles size={20} />
                                    Generate AI Image
                                </button>
                            )}
                        </div>
                    ) : isQuote ? (
                        <blockquote
                            contentEditable
                            suppressContentEditableWarning
                            className="block-quote"
                            onBlur={(e) => handleUpdateBlock(block.id, e.currentTarget.textContent || '')}
                        >
                            {block.content}
                        </blockquote>
                    ) : isCode ? (
                        <pre className="block-code">
                            <code
                                contentEditable
                                suppressContentEditableWarning
                                onBlur={(e) => handleUpdateBlock(block.id, e.currentTarget.textContent || '')}
                            >
                                {block.content}
                            </code>
                        </pre>
                    ) : (
                        <div
                            contentEditable
                            suppressContentEditableWarning
                            className={`block-editable ${isHeading ? 'heading' : ''} ${isBullet ? 'bullet' : ''}`}
                            onBlur={(e) => handleUpdateBlock(block.id, e.currentTarget.textContent || '')}
                            data-placeholder={isBullet ? '• List item...' : 'Type something...'}
                        >
                            {isBullet ? `• ${block.content}` : block.content}
                        </div>
                    )}
                </div>

                <button
                    className="block-delete"
                    onClick={() => handleDeleteBlock(block.id)}
                    title="Delete block"
                >
                    <Trash2 size={14} />
                </button>
            </div>
        );
    };

    if (!currentSlide) {
        return <div className="block-editor">Loading...</div>;
    }

    return (
        <div className="block-editor">
            {/* Editor Header */}
            <div className="editor-header">
                <div className="slide-nav">
                    <button
                        onClick={prevSlide}
                        disabled={currentSlideIndex === 0}
                    >
                        <ChevronLeft size={18} />
                    </button>
                    <span className="slide-counter">
                        Slide {currentSlideIndex + 1} of {slides.length}
                    </span>
                    <button
                        onClick={nextSlide}
                        disabled={currentSlideIndex === slides.length - 1}
                    >
                        <ChevronRight size={18} />
                    </button>
                </div>

                <div className="editor-actions">
                    <button className="btn-icon" onClick={handleAddSlide} title="Add Slide">
                        <Plus size={18} />
                        Add Slide
                    </button>
                    <button className="btn-icon danger" onClick={handleDeleteSlide} title="Delete Slide">
                        <Trash2 size={18} />
                    </button>
                    <button className="btn-icon" onClick={handlePreview} title="Preview">
                        <Eye size={18} />
                        Preview
                    </button>
                    <button className="btn-primary" onClick={handleSave}>
                        <Save size={18} />
                        Save
                    </button>
                </div>
            </div>

            {/* Main Editor Container */}
            <div className="editor-main">
                {/* Slide Thumbnails */}
                <div className="slide-thumbnails">
                    {slides.map((slide, index) => (
                        <div
                            key={slide.id}
                            className={`slide-thumb ${index === currentSlideIndex ? 'active' : ''}`}
                            onClick={() => goToSlide(index)}
                        >
                            <span className="thumb-number">{index + 1}</span>
                            <div className="thumb-preview">
                                {slide.blocks[0]?.content?.substring(0, 20) || 'Empty'}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Main Editor Area */}
                <div className="editor-canvas">
                    <div className="slide-canvas">
                        {currentSlide.blocks.map((block, index) => renderBlock(block, index))}

                        {/* Add Block Button */}
                        <div className="add-block-container">
                            <button
                                className="add-block-btn"
                                onClick={() => setShowBlockMenu(!showBlockMenu)}
                            >
                                <Plus size={20} />
                                Add Block
                            </button>

                            {showBlockMenu && (
                                <div className="block-menu">
                                    {BLOCK_TYPES.map(({ type, icon, label }) => (
                                        <button
                                            key={type}
                                            className="block-menu-item"
                                            onClick={() => handleAddBlock(type)}
                                        >
                                            {icon}
                                            <span>{label}</span>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* AI Image Generator Modal */}
            {showImageGenerator && (
                <ImageGenerator
                    slideTitle={currentSlide.blocks.find(b => b.type === 'heading')?.content || 'Untitled'}
                    slideContent={currentSlide.blocks.map(b => b.content).join(' ').substring(0, 200)}
                    onImageGenerated={handleImageGenerated}
                    onClose={() => {
                        setShowImageGenerator(false);
                        setActiveImageBlockId(null);
                    }}
                />
            )}
        </div>
    );
};

/**
 * BlockEditor component wrapped with PresentationProvider.
 * This is the main export that should be used in the application.
 */
export const BlockEditor: React.FC<BlockEditorProps> = ({
    initialSlides,
    onSave,
    onPreview
}) => {
    return (
        <PresentationProvider initialSlides={initialSlides}>
            <BlockEditorInternal onSave={onSave} onPreview={onPreview} />
        </PresentationProvider>
    );
};

export default BlockEditor;
