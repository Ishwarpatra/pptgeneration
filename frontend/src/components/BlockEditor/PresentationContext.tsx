/**
 * Presentation State Context
 * 
 * Global state management for the slide deck using React Context.
 * Provides centralized access to slides, current selection, and actions.
 */
import React, { createContext, useContext, useReducer, useCallback, type ReactNode } from 'react';
import type { Block, Slide, BlockType } from './types';

// ============================================================================
// Types
// ============================================================================

interface PresentationState {
    slides: Slide[];
    currentSlideIndex: number;
    isDirty: boolean;
    lastSavedAt: Date | null;
}

type PresentationAction =
    | { type: 'SET_SLIDES'; payload: Slide[] }
    | { type: 'ADD_SLIDE'; payload?: { layout?: Slide['layout'] } }
    | { type: 'DELETE_SLIDE'; payload: number }
    | { type: 'SET_CURRENT_SLIDE'; payload: number }
    | { type: 'UPDATE_SLIDE'; payload: { index: number; slide: Slide } }
    | { type: 'ADD_BLOCK'; payload: { slideIndex: number; block: Block } }
    | { type: 'UPDATE_BLOCK'; payload: { slideIndex: number; blockId: string; content: string } }
    | { type: 'UPDATE_BLOCK_METADATA'; payload: { slideIndex: number; blockId: string; metadata: Record<string, unknown> } }
    | { type: 'DELETE_BLOCK'; payload: { slideIndex: number; blockId: string } }
    | { type: 'REORDER_BLOCKS'; payload: { slideIndex: number; fromIndex: number; toIndex: number } }
    | { type: 'MARK_SAVED' }
    | { type: 'RESET' };

interface PresentationContextType {
    state: PresentationState;
    dispatch: React.Dispatch<PresentationAction>;
    // Convenience methods
    currentSlide: Slide | null;
    addSlide: (layout?: Slide['layout']) => void;
    deleteSlide: (index?: number) => void;
    goToSlide: (index: number) => void;
    nextSlide: () => void;
    prevSlide: () => void;
    addBlock: (block: Block) => void;
    updateBlock: (blockId: string, content: string) => void;
    updateBlockMetadata: (blockId: string, metadata: Record<string, unknown>) => void;
    deleteBlock: (blockId: string) => void;
    reorderBlocks: (fromIndex: number, toIndex: number) => void;
    getSlides: () => Slide[];
    markSaved: () => void;
}

// ============================================================================
// Utilities
// ============================================================================

/**
 * Generate a cryptographically random UUID.
 * Uses crypto.randomUUID() for production-quality unique identifiers.
 */
export const generateId = (): string => {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID();
    }
    // Fallback for older browsers (still better than Math.random)
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
};

export const createBlock = (type: BlockType, content: string = ''): Block => ({
    id: generateId(),
    type,
    content,
    metadata: type === 'heading' ? { level: 1 } : {}
});

export const createSlide = (layout: Slide['layout'] = 'content'): Slide => ({
    id: generateId(),
    blocks: [createBlock('heading', 'New Slide')],
    layout,
});

// ============================================================================
// Reducer
// ============================================================================

const initialState: PresentationState = {
    slides: [createSlide('title')],
    currentSlideIndex: 0,
    isDirty: false,
    lastSavedAt: null,
};

function presentationReducer(state: PresentationState, action: PresentationAction): PresentationState {
    switch (action.type) {
        case 'SET_SLIDES':
            return {
                ...state,
                slides: action.payload,
                currentSlideIndex: Math.min(state.currentSlideIndex, action.payload.length - 1),
                isDirty: true,
            };

        case 'ADD_SLIDE': {
            const newSlide = createSlide(action.payload?.layout || 'content');
            return {
                ...state,
                slides: [...state.slides, newSlide],
                currentSlideIndex: state.slides.length,
                isDirty: true,
            };
        }

        case 'DELETE_SLIDE': {
            if (state.slides.length <= 1) return state;
            const newSlides = state.slides.filter((_, i) => i !== action.payload);
            return {
                ...state,
                slides: newSlides,
                currentSlideIndex: Math.max(0, Math.min(state.currentSlideIndex, newSlides.length - 1)),
                isDirty: true,
            };
        }

        case 'SET_CURRENT_SLIDE':
            return {
                ...state,
                currentSlideIndex: Math.max(0, Math.min(action.payload, state.slides.length - 1)),
            };

        case 'UPDATE_SLIDE': {
            const newSlides = state.slides.map((slide, i) =>
                i === action.payload.index ? action.payload.slide : slide
            );
            return {
                ...state,
                slides: newSlides,
                isDirty: true,
            };
        }

        case 'ADD_BLOCK': {
            const { slideIndex, block } = action.payload;
            const slide = state.slides[slideIndex];
            if (!slide) return state;

            const updatedSlide: Slide = {
                ...slide,
                blocks: [...slide.blocks, block],
            };

            return {
                ...state,
                slides: state.slides.map((s, i) => i === slideIndex ? updatedSlide : s),
                isDirty: true,
            };
        }

        case 'UPDATE_BLOCK': {
            const { slideIndex, blockId, content } = action.payload;
            const slide = state.slides[slideIndex];
            if (!slide) return state;

            const updatedSlide: Slide = {
                ...slide,
                blocks: slide.blocks.map(b =>
                    b.id === blockId ? { ...b, content } : b
                ),
            };

            return {
                ...state,
                slides: state.slides.map((s, i) => i === slideIndex ? updatedSlide : s),
                isDirty: true,
            };
        }

        case 'UPDATE_BLOCK_METADATA': {
            const { slideIndex, blockId, metadata } = action.payload;
            const slide = state.slides[slideIndex];
            if (!slide) return state;

            const updatedSlide: Slide = {
                ...slide,
                blocks: slide.blocks.map(b =>
                    b.id === blockId ? { ...b, metadata: { ...b.metadata, ...metadata } } : b
                ),
            };

            return {
                ...state,
                slides: state.slides.map((s, i) => i === slideIndex ? updatedSlide : s),
                isDirty: true,
            };
        }

        case 'DELETE_BLOCK': {
            const { slideIndex, blockId } = action.payload;
            const slide = state.slides[slideIndex];
            if (!slide || slide.blocks.length <= 1) return state;

            const updatedSlide: Slide = {
                ...slide,
                blocks: slide.blocks.filter(b => b.id !== blockId),
            };

            return {
                ...state,
                slides: state.slides.map((s, i) => i === slideIndex ? updatedSlide : s),
                isDirty: true,
            };
        }

        case 'REORDER_BLOCKS': {
            const { slideIndex, fromIndex, toIndex } = action.payload;
            const slide = state.slides[slideIndex];
            if (!slide) return state;

            const newBlocks = [...slide.blocks];
            const [movedBlock] = newBlocks.splice(fromIndex, 1);
            newBlocks.splice(toIndex, 0, movedBlock);

            const updatedSlide: Slide = {
                ...slide,
                blocks: newBlocks,
            };

            return {
                ...state,
                slides: state.slides.map((s, i) => i === slideIndex ? updatedSlide : s),
                isDirty: true,
            };
        }

        case 'MARK_SAVED':
            return {
                ...state,
                isDirty: false,
                lastSavedAt: new Date(),
            };

        case 'RESET':
            return initialState;

        default:
            return state;
    }
}

// ============================================================================
// Context
// ============================================================================

const PresentationContext = createContext<PresentationContextType | null>(null);

interface PresentationProviderProps {
    children: ReactNode;
    initialSlides?: Slide[];
}

export function PresentationProvider({ children, initialSlides }: PresentationProviderProps) {
    const [state, dispatch] = useReducer(
        presentationReducer,
        initialSlides
            ? { ...initialState, slides: initialSlides }
            : initialState
    );

    const currentSlide = state.slides[state.currentSlideIndex] || null;

    const addSlide = useCallback((layout?: Slide['layout']) => {
        dispatch({ type: 'ADD_SLIDE', payload: { layout } });
    }, []);

    const deleteSlide = useCallback((index?: number) => {
        dispatch({ type: 'DELETE_SLIDE', payload: index ?? state.currentSlideIndex });
    }, [state.currentSlideIndex]);

    const goToSlide = useCallback((index: number) => {
        dispatch({ type: 'SET_CURRENT_SLIDE', payload: index });
    }, []);

    const nextSlide = useCallback(() => {
        if (state.currentSlideIndex < state.slides.length - 1) {
            dispatch({ type: 'SET_CURRENT_SLIDE', payload: state.currentSlideIndex + 1 });
        }
    }, [state.currentSlideIndex, state.slides.length]);

    const prevSlide = useCallback(() => {
        if (state.currentSlideIndex > 0) {
            dispatch({ type: 'SET_CURRENT_SLIDE', payload: state.currentSlideIndex - 1 });
        }
    }, [state.currentSlideIndex]);

    const addBlock = useCallback((block: Block) => {
        dispatch({
            type: 'ADD_BLOCK',
            payload: { slideIndex: state.currentSlideIndex, block }
        });
    }, [state.currentSlideIndex]);

    const updateBlock = useCallback((blockId: string, content: string) => {
        dispatch({
            type: 'UPDATE_BLOCK',
            payload: { slideIndex: state.currentSlideIndex, blockId, content }
        });
    }, [state.currentSlideIndex]);

    const updateBlockMetadata = useCallback((blockId: string, metadata: Record<string, unknown>) => {
        dispatch({
            type: 'UPDATE_BLOCK_METADATA',
            payload: { slideIndex: state.currentSlideIndex, blockId, metadata }
        });
    }, [state.currentSlideIndex]);

    const deleteBlock = useCallback((blockId: string) => {
        dispatch({
            type: 'DELETE_BLOCK',
            payload: { slideIndex: state.currentSlideIndex, blockId }
        });
    }, [state.currentSlideIndex]);

    const reorderBlocks = useCallback((fromIndex: number, toIndex: number) => {
        dispatch({
            type: 'REORDER_BLOCKS',
            payload: { slideIndex: state.currentSlideIndex, fromIndex, toIndex }
        });
    }, [state.currentSlideIndex]);

    const getSlides = useCallback(() => state.slides, [state.slides]);

    const markSaved = useCallback(() => {
        dispatch({ type: 'MARK_SAVED' });
    }, []);

    const contextValue: PresentationContextType = {
        state,
        dispatch,
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
        markSaved,
    };

    return (
        <PresentationContext.Provider value={contextValue}>
            {children}
        </PresentationContext.Provider>
    );
}

// ============================================================================
// Hook
// ============================================================================

export function usePresentation(): PresentationContextType {
    const context = useContext(PresentationContext);
    if (!context) {
        throw new Error('usePresentation must be used within a PresentationProvider');
    }
    return context;
}

export type { PresentationState, PresentationAction, PresentationContextType };
