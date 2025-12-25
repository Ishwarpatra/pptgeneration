// Block Editor Type Definitions

export type BlockType = 'heading' | 'text' | 'bullet' | 'image' | 'divider' | 'quote' | 'code';

export interface Block {
    id: string;
    type: BlockType;
    content: string;
    metadata?: {
        level?: 1 | 2 | 3;  // For headings
        imageUrl?: string;   // For images
        language?: string;   // For code blocks
        align?: 'left' | 'center' | 'right';
    };
}

export interface Slide {
    id: string;
    blocks: Block[];
    layout: 'title' | 'content' | 'two-column' | 'image-left' | 'image-right' | 'blank';
    notes?: string;
}

export interface Presentation {
    id: string;
    title: string;
    slides: Slide[];
    styleId: string;
    createdAt: string;
    updatedAt: string;
}

export interface DragItem {
    type: 'block';
    id: string;
    index: number;
}
