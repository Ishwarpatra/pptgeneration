// Template Library Type Definitions

export interface Template {
    id: string;
    name: string;
    description: string;
    thumbnail: string;
    category: TemplateCategory;
    styleId: string;
    slideCount: number;
    isPremium: boolean;
    colors: string[];
}

export type TemplateCategory =
    | 'business'
    | 'education'
    | 'creative'
    | 'technology'
    | 'minimal'
    | 'marketing';

export interface TemplateFilter {
    category?: TemplateCategory;
    isPremium?: boolean;
    searchQuery?: string;
}
