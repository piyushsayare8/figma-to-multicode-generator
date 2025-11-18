"""
Intermediate Layout Schema (ILS) Builder - UPGRADED.

This module converts classified UI blocks + style info into a structured 
intermediate representation that can be used to generate code across 
multiple frameworks.

Now includes:
  - Page-level style (colors, spacing, layout_mode)
  - Section-level style (padding, gap, alignment, border_radius)
  - Integration with style_analyzer.py output
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from config import Config, ILS_VERSION, DEFAULT_PAGE_TITLE

logger = logging.getLogger(__name__)

class SectionType(Enum):
    """Enumeration of supported section types."""
    FORM = "form"
    CARDS = "cards"
    HERO = "hero"
    HEADER = "header"
    FOOTER = "footer"
    NAVIGATION = "navigation"
    CONTENT = "content"
    GALLERY = "gallery"
    UNKNOWN = "unknown"

class ElementType(Enum):
    """Enumeration of supported UI element types."""
    TEXT_INPUT = "text_input"
    PASSWORD_INPUT = "password_input"
    EMAIL_INPUT = "email_input"
    BUTTON = "button"
    LINK = "link"
    TEXT_BLOCK = "text_block"
    IMAGE_BLOCK = "image_block"
    CARD = "card"
    CHECKBOX = "checkbox"
    RADIO_BUTTON = "radio_button"
    SELECT_DROPDOWN = "select_dropdown"
    TEXTAREA = "textarea"
    LABEL = "label"

@dataclass
class UIElement:
    """Represents a single UI element in the ILS."""
    type: str
    label: Optional[str] = None
    name: Optional[str] = None
    placeholder: Optional[str] = None
    value: Optional[str] = None
    required: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Section:
    """Represents a section of the UI (form, cards, etc.) with style."""
    type: str
    id: str
    title: Optional[str] = None
    elements: List[UIElement] = None
    primary_action: Optional[UIElement] = None
    secondary_actions: List[UIElement] = None
    style: Optional[Dict[str, Any]] = None  # NEW: section-level style
    fields: List[Dict[str, Any]] = None      # NEW: for forms (alias of elements)
    cards: List[Dict[str, Any]] = None       # NEW: for card sections
    
    def __post_init__(self):
        if self.elements is None:
            self.elements = []
        if self.secondary_actions is None:
            self.secondary_actions = []
        if self.style is None:
            self.style = {}
        if self.fields is None:
            self.fields = []
        if self.cards is None:
            self.cards = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "type": self.type,
            "id": self.id
        }
        
        if self.title:
            result["title"] = self.title
        
        # Style is always included now
        if self.style:
            result["style"] = self.style
            
        # Use 'fields' for forms, 'elements' for generic
        if self.type == SectionType.FORM.value and self.elements:
            result["fields"] = [elem.to_dict() for elem in self.elements]
        elif self.elements:
            result["elements"] = [elem.to_dict() for elem in self.elements]
        
        # Use 'cards' for card sections
        if self.type == SectionType.CARDS.value and self.cards:
            result["cards"] = self.cards
            
        if self.primary_action:
            result["primary_action"] = self.primary_action.to_dict()
            
        if self.secondary_actions:
            result["secondary_actions"] = [action.to_dict() for action in self.secondary_actions]
            
        return result

@dataclass
class ILS:
    """Intermediate Layout Schema representation with style."""
    version: str = ILS_VERSION
    type: str = "page"
    title: str = DEFAULT_PAGE_TITLE
    layout_mode: str = "single_column"  # NEW: single_column | two_column | grid | centered_form
    style: Optional[Dict[str, Any]] = None  # NEW: page-level style
    sections: List[Section] = None
    
    def __post_init__(self):
        if self.sections is None:
            self.sections = []
        if self.style is None:
            self.style = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "version": self.version,
            "type": self.type,
            "title": self.title,
            "layout_mode": self.layout_mode
        }
        
        # Include page-level style
        if self.style:
            result["style"] = self.style
        
        result["sections"] = [section.to_dict() for section in self.sections]
        
        return result

class ILSBuilder:
    """Builder class for constructing ILS from classified blocks."""
    
    def __init__(self):
        self.blocks = []
        self.sections = []
        
    def analyze_layout_patterns(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze blocks to identify common layout patterns.
        
        Returns:
            Dictionary containing layout analysis results
        """
        if not blocks:
            return {"pattern": "empty", "confidence": 1.0}
        
        # Count element types
        type_counts = {}
        for block in blocks:
            block_type = block.get('type', 'unknown')
            type_counts[block_type] = type_counts.get(block_type, 0) + 1
        
        # Analyze spatial relationships
        input_count = type_counts.get('input_field', 0) + type_counts.get('password_input', 0)
        button_count = type_counts.get('button', 0)
        text_count = type_counts.get('text_block', 0)
        card_count = type_counts.get('card', 0)
        
        # Determine primary pattern
        if input_count >= 2 and button_count >= 1:
            return {"pattern": "form", "confidence": 0.8}
        elif card_count >= 2:
            return {"pattern": "cards", "confidence": 0.7}
        elif text_count >= 3:
            return {"pattern": "content", "confidence": 0.6}
        elif button_count >= 2:
            return {"pattern": "navigation", "confidence": 0.5}
        else:
            return {"pattern": "generic", "confidence": 0.4}
    
    def group_blocks_by_proximity(self, blocks: List[Dict[str, Any]], threshold: int = 50) -> List[List[Dict[str, Any]]]:
        """
        Group blocks that are close to each other spatially.
        
        Args:
            blocks: List of UI blocks
            threshold: Maximum distance for grouping
            
        Returns:
            List of block groups
        """
        if not blocks:
            return []
        
        # Sort blocks by vertical position first
        sorted_blocks = sorted(blocks, key=lambda b: (b['y'], b['x']))
        
        groups = []
        current_group = [sorted_blocks[0]]
        
        for block in sorted_blocks[1:]:
            # Check if block is close to any block in current group
            close_to_group = False
            for group_block in current_group:
                distance = self.calculate_block_distance(block, group_block)
                if distance <= threshold:
                    close_to_group = True
                    break
            
            if close_to_group:
                current_group.append(block)
            else:
                groups.append(current_group)
                current_group = [block]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def calculate_block_distance(self, block1: Dict[str, Any], block2: Dict[str, Any]) -> float:
        """Calculate the minimum distance between two blocks."""
        x1, y1, w1, h1 = block1['x'], block1['y'], block1['w'], block1['h']
        x2, y2, w2, h2 = block2['x'], block2['y'], block2['w'], block2['h']
        
        # Calculate center points
        center1_x, center1_y = x1 + w1/2, y1 + h1/2
        center2_x, center2_y = x2 + w2/2, y2 + h2/2
        
        # Euclidean distance between centers
        return ((center1_x - center2_x)**2 + (center1_y - center2_y)**2)**0.5
    
    def create_form_section(self, blocks: List[Dict[str, Any]], section_id: str, 
                           style_info: Optional[Dict[str, Any]] = None) -> Section:
        """Create a form section from a group of blocks with style."""
        elements = []
        primary_action = None
        secondary_actions = []
        
        # Sort blocks by position (top to bottom, left to right)
        sorted_blocks = sorted(blocks, key=lambda b: (b['y'], b['x']))
        
        for i, block in enumerate(sorted_blocks):
            block_type = block.get('type', 'unknown')
            
            if block_type in ['input_field', 'password_input', 'text_input']:
                # Determine input type
                input_type = ElementType.PASSWORD_INPUT.value if block_type == 'password_input' else ElementType.TEXT_INPUT.value
                
                # Generate label based on position and context
                label = self.generate_label_for_input(block, i, sorted_blocks)
                name = self.generate_name_for_input(input_type, i)
                placeholder = self.generate_placeholder_for_input(input_type)
                
                element = UIElement(
                    type=input_type,
                    label=label,
                    name=name,
                    placeholder=placeholder,
                    required=True
                )
                elements.append(element)
                
            elif block_type == 'button':
                button_text = self.generate_button_text(block, i, len(sorted_blocks))
                button_element = UIElement(
                    type=ElementType.BUTTON.value,
                    label=button_text
                )
                
                # Determine if primary or secondary action
                if primary_action is None and i > len(sorted_blocks) // 2:
                    primary_action = button_element
                else:
                    secondary_actions.append(button_element)
                    
            elif block_type == 'text_block' or block_type == 'text':
                # Add as label or description
                text_content = self.generate_text_content(block, i)
                if text_content:
                    element = UIElement(
                        type=ElementType.TEXT_BLOCK.value,
                        label=text_content
                    )
                    elements.append(element)
        
        # Ensure we have a primary action
        if primary_action is None and elements:
            primary_action = UIElement(
                type=ElementType.BUTTON.value,
                label="Submit"
            )
        
        # Build section style from style_info
        section_style = self._build_section_style(
            blocks, style_info, section_type="form"
        )
        
        return Section(
            type=SectionType.FORM.value,
            id=section_id,
            title=None,  # Forms typically don't have titles
            elements=elements,
            primary_action=primary_action,
            secondary_actions=secondary_actions,
            style=section_style
        )
    
    def create_cards_section(self, blocks: List[Dict[str, Any]], section_id: str,
                            style_info: Optional[Dict[str, Any]] = None) -> Section:
        """Create a cards section from a group of blocks with style."""
        cards = []
        
        # Group blocks into individual cards based on proximity
        card_groups = self.group_blocks_by_proximity(blocks, threshold=30)
        
        for i, card_blocks in enumerate(card_groups):
            card_dict = {
                "title": f"Card {i + 1}",
                "body": "Auto-generated content."
            }
            cards.append(card_dict)
        
        # Build section style
        section_style = self._build_section_style(
            blocks, style_info, section_type="cards"
        )
        
        # Detect column count from horizontal positioning
        if len(blocks) >= 3:
            x_positions = sorted([b['x'] for b in blocks])
            unique_x = []
            for x in x_positions:
                if not unique_x or abs(x - unique_x[-1]) > 40:
                    unique_x.append(x)
            section_style["columns"] = min(len(unique_x), 4)
        else:
            section_style["columns"] = len(cards) if len(cards) <= 3 else 3
        
        return Section(
            type=SectionType.CARDS.value,
            id=section_id,
            title=None,
            elements=[],
            cards=cards,
            style=section_style
        )
    
    def create_content_section(self, blocks: List[Dict[str, Any]], section_id: str,
                              style_info: Optional[Dict[str, Any]] = None) -> Section:
        """Create a content section from a group of blocks with style."""
        elements = []
        
        sorted_blocks = sorted(blocks, key=lambda b: (b['y'], b['x']))
        
        for i, block in enumerate(sorted_blocks):
            block_type = block.get('type', 'unknown')
            
            if block_type in ['text_block', 'text', 'heading']:
                text_content = self.generate_text_content(block, i)
                element = UIElement(
                    type=ElementType.TEXT_BLOCK.value,
                    label=text_content
                )
                elements.append(element)
                
            elif block_type in ['image_block', 'image']:
                element = UIElement(
                    type=ElementType.IMAGE_BLOCK.value,
                    label="Image",
                    value="placeholder-image.jpg"
                )
                elements.append(element)
        
        # Build section style
        section_style = self._build_section_style(
            blocks, style_info, section_type="content"
        )
        
        return Section(
            type=SectionType.CONTENT.value,
            id=section_id,
            title=None,
            elements=elements,
            style=section_style
        )
    
    def generate_label_for_input(self, block: Dict[str, Any], index: int, all_blocks: List[Dict[str, Any]]) -> str:
        """Generate a meaningful label for an input field."""
        block_type = block.get('type', 'unknown')
        
        if block_type == 'password_input':
            return "Password"
        
        # Look for common patterns based on position
        if index == 0 or any('email' in str(b).lower() for b in all_blocks[:index+1]):
            return "Email"
        elif index == 1 and block_type == 'input_field':
            return "Username"
        else:
            return f"Field {index + 1}"
    
    def generate_name_for_input(self, input_type: str, index: int) -> str:
        """Generate a valid name attribute for an input."""
        if input_type == ElementType.PASSWORD_INPUT.value:
            return "password"
        elif input_type == ElementType.EMAIL_INPUT.value:
            return "email"
        elif index == 0:
            return "email"  # First input is often email
        else:
            return f"field_{index}"
    
    def generate_placeholder_for_input(self, input_type: str) -> str:
        """Generate appropriate placeholder text."""
        placeholders = {
            ElementType.EMAIL_INPUT.value: "Enter your email",
            ElementType.PASSWORD_INPUT.value: "Enter your password",
            ElementType.TEXT_INPUT.value: "Enter text here"
        }
        return placeholders.get(input_type, "Enter value")
    
    def generate_button_text(self, block: Dict[str, Any], index: int, total_count: int) -> str:
        """Generate appropriate button text based on context."""
        # If it's likely the main action button
        if index >= total_count - 2:
            return "Submit"
        else:
            return "Cancel"
    
    def generate_text_content(self, block: Dict[str, Any], index: int) -> str:
        """Generate text content for text blocks."""
        area = block.get('w', 0) * block.get('h', 0)
        
        if area > 5000:
            return "This is a larger text block with more content."
        elif index == 0:
            return "Welcome! Please fill out the form below."
        else:
            return f"Text content {index + 1}"
    
    def _build_section_style(self, blocks: List[Dict[str, Any]], 
                            style_info: Optional[Dict[str, Any]], 
                            section_type: str) -> Dict[str, Any]:
        """
        Build section-level style from style_info and block positions.
        
        Args:
            blocks: Blocks in this section
            style_info: Global style info from style_analyzer
            section_type: "form" | "cards" | "content"
            
        Returns:
            Dict with section style properties
        """
        section_style = {}
        
        # Get base spacing from style_info
        base_spacing = 16
        if style_info and 'page' in style_info:
            base_spacing = style_info['page'].get('base_spacing', 16)
        
        # Section-specific defaults
        if section_type == "form":
            section_style.update({
                "card": True,
                "border_radius": 16,
                "padding": base_spacing * 1.5,  # 24px if base is 16
                "gap": base_spacing,
                "alignment": "center"
            })
        elif section_type == "cards":
            section_style.update({
                "border_radius": 12,
                "padding": base_spacing,
                "gap": base_spacing,
                "columns": 3  # Will be overridden in create_cards_section
            })
        else:  # content
            section_style.update({
                "padding": base_spacing,
                "gap": base_spacing * 0.75,
                "alignment": "left"
            })
        
        return section_style


def build_ils(typed_blocks: List[Dict[str, Any]], 
              style_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build an Intermediate Layout Schema from typed blocks + style info.
    
    This is the main function that converts classified UI blocks and extracted
    style information into a structured representation for code generation.
    
    Args:
        typed_blocks: List of blocks with type classification
        style_info: Optional style analysis output from style_analyzer.analyze_style()
        
    Returns:
        Dictionary representation of the ILS with structure + style
    """
    logger.debug(f"Building ILS from {len(typed_blocks)} typed blocks")
    
    if not typed_blocks:
        # Return minimal empty page
        empty_ils = ILS(
            title="Empty Page",
            layout_mode="single_column",
            style=_get_default_page_style(style_info)
        )
        return empty_ils.to_dict()
    
    builder = ILSBuilder()
    builder.blocks = typed_blocks
    
    # Analyze layout patterns
    layout_analysis = builder.analyze_layout_patterns(typed_blocks)
    logger.debug(f"Layout pattern: {layout_analysis}")
    
    # Group blocks by proximity
    block_groups = builder.group_blocks_by_proximity(typed_blocks)
    logger.debug(f"Grouped into {len(block_groups)} sections")
    
    sections = []
    
    for i, group in enumerate(block_groups):
        section_id = f"auto_{layout_analysis['pattern']}_{i + 1}"
        group_pattern = builder.analyze_layout_patterns(group)
        
        if group_pattern["pattern"] == "form":
            section = builder.create_form_section(group, section_id, style_info)
        elif group_pattern["pattern"] == "cards":
            section = builder.create_cards_section(group, section_id, style_info)
        else:
            section = builder.create_content_section(group, section_id, style_info)
        
        sections.append(section)
    
    # Ensure we have at least one section
    if not sections:
        # Create a generic section with default style
        base_spacing = 16
        if style_info and 'page' in style_info:
            base_spacing = style_info['page'].get('base_spacing', 16)
        
        section = Section(
            type=SectionType.CONTENT.value,
            id="auto_content_1",
            title=None,
            elements=[
                UIElement(
                    type=ElementType.TEXT_BLOCK.value,
                    label="Generated content from UI analysis"
                )
            ],
            style={
                "padding": base_spacing,
                "gap": base_spacing * 0.75
            }
        )
        sections.append(section)
    
    # Determine layout mode from style_info
    layout_mode = "single_column"
    if style_info and 'page' in style_info:
        layout_mode = style_info['page'].get('layout_mode', 'single_column')
    
    # Build page-level style
    page_style = _get_page_style(style_info)
    
    # Build final ILS
    ils = ILS(
        title="Generated UI",
        layout_mode=layout_mode,
        style=page_style,
        sections=sections
    )
    
    ils_dict = ils.to_dict()
    logger.info(f"Built ILS with {len(sections)} sections, layout_mode={layout_mode}")
    
    return ils_dict


def _get_default_page_style(style_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Get default page style when no blocks are detected."""
    if style_info and 'page' in style_info:
        return {
            "background_color": style_info['page'].get('background_color', '#f5f6fa'),
            "primary_color": style_info['page'].get('primary_color', '#2563eb'),
            "accent_color": style_info['page'].get('accent_color', '#f59e0b'),
            "text_color": style_info['page'].get('text_color', '#111827')
        }
    
    return {
        "background_color": "#f5f6fa",
        "primary_color": "#2563eb",
        "accent_color": "#f59e0b",
        "text_color": "#111827"
    }


def _get_page_style(style_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract page-level style from style_info."""
    if not style_info or 'page' not in style_info:
        return _get_default_page_style(None)
    
    page_info = style_info['page']
    
    return {
        "background_color": page_info.get('background_color', '#f5f6fa'),
        "primary_color": page_info.get('primary_color', '#2563eb'),
        "accent_color": page_info.get('accent_color', '#f59e0b'),
        "text_color": page_info.get('text_color', '#111827'),
        "base_spacing": page_info.get('base_spacing', 16)
    }

