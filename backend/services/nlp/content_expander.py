"""
NLP Content Expansion Service.
Uses LangChain with structured output to generate presentation outlines from topics.
"""
import os
from typing import Optional
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from .models import (
    PresentationOutline,
    SlideContent,
    VisualSpec,
    VisualType,
    LayoutType,
    ContentExpansionRequest,
)

load_dotenv()


class ContentExpander:
    """
    Hierarchical content expansion engine.
    Transforms topics into structured presentation outlines with visual specifications.
    """

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7):
        """
        Initialize the content expander.
        
        Args:
            model_name: OpenAI model to use (gpt-4o-mini recommended for cost/quality)
            temperature: Creativity level (0.0-1.0)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.parser = PydanticOutputParser(pydantic_object=PresentationOutline)

    def _build_system_prompt(self) -> str:
        """Build the system prompt for presentation generation."""
        return """You are an expert presentation designer and content strategist.
Your task is to create comprehensive, well-structured presentation outlines.

Guidelines:
1. Each slide should have ONE clear key message
2. Body text should be concise bullet points (3-5 per slide)
3. Suggest appropriate visuals for each slide (charts, images, 3D icons)
4. Include meaningful speaker notes with talking points
5. Maintain narrative flow between slides
6. Start with a compelling opening, end with a strong conclusion

For visual specifications:
- Use chart_bar, chart_pie, chart_line for data presentations
- Use image for conceptual or illustrative content
- Use icon_3d for abstract concepts or section headers
- Use diagram for processes or relationships

Always ensure the content is professional and audience-appropriate."""

    def _build_generation_prompt(self) -> ChatPromptTemplate:
        """Build the generation prompt template."""
        return ChatPromptTemplate.from_messages([
            ("system", self._build_system_prompt()),
            ("human", """Create a presentation outline for the following:

Topic: {topic}
Number of slides: {num_slides}
{context_section}
{style_section}

{format_instructions}

Generate a complete, professional presentation outline.""")
        ])

    async def expand_content(
        self,
        request: ContentExpansionRequest
    ) -> PresentationOutline:
        """
        Expand a topic into a full presentation outline.
        
        Args:
            request: Content expansion request with topic and parameters
            
        Returns:
            Structured PresentationOutline with all slide specifications
        """
        # Build context and style sections
        context_section = ""
        if request.context:
            context_section = f"Additional context: {request.context}"
        
        style_section = ""
        if request.style_preference:
            style_section = f"Preferred style: {request.style_preference}"

        # Build the chain
        prompt = self._build_generation_prompt()
        chain = prompt | self.llm | self.parser

        # Generate the outline
        result = await chain.ainvoke({
            "topic": request.topic,
            "num_slides": request.num_slides,
            "context_section": context_section,
            "style_section": style_section,
            "format_instructions": self.parser.get_format_instructions(),
        })

        return result

    def expand_content_sync(
        self,
        request: ContentExpansionRequest
    ) -> PresentationOutline:
        """
        Synchronous version of expand_content for non-async contexts.
        """
        import asyncio
        return asyncio.run(self.expand_content(request))


class SlideContentEnhancer:
    """
    Enhances individual slides with more detailed content.
    Used for iterative refinement after initial outline generation.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.5,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.parser = PydanticOutputParser(pydantic_object=SlideContent)

    async def enhance_slide(
        self,
        slide: SlideContent,
        presentation_context: str
    ) -> SlideContent:
        """
        Enhance a slide with more detailed content.
        
        Args:
            slide: Original slide content
            presentation_context: Overall presentation theme/topic
            
        Returns:
            Enhanced SlideContent with richer details
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are enhancing slide content for a presentation.
Make the content more impactful and detailed while keeping it concise.
Improve the visual specification to better support the message."""),
            ("human", """Presentation context: {context}

Current slide:
- Title: {title}
- Body: {body}
- Key message: {key_message}

Enhance this slide with better content and visual suggestions.

{format_instructions}""")
        ])

        chain = prompt | self.llm | self.parser

        result = await chain.ainvoke({
            "context": presentation_context,
            "title": slide.title,
            "body": "\n".join(slide.body_text),
            "key_message": slide.key_message,
            "format_instructions": self.parser.get_format_instructions(),
        })

        return result


# Convenience function for quick generation
async def generate_presentation(
    topic: str,
    num_slides: int = 5,
    context: Optional[str] = None,
    style: Optional[str] = None
) -> PresentationOutline:
    """
    Quick function to generate a presentation outline.
    
    Args:
        topic: Main presentation topic
        num_slides: Number of slides (3-50)
        context: Additional context or content
        style: Visual style preference
        
    Returns:
        Complete PresentationOutline
    """
    expander = ContentExpander()
    request = ContentExpansionRequest(
        topic=topic,
        num_slides=num_slides,
        context=context,
        style_preference=style,
    )
    return await expander.expand_content(request)
