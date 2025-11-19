"""
ILS v2: Intermediate Layout Schema - Tree-Based, Layout-Aware, Semantic

This module builds a hierarchical tree representation of UI layouts from
detected and classified blocks. The tree structure enables better code
generation with proper nesting, semantic sections, and layout modes.

Architecture:
- ILSNode: Base tree node with layout, style, and children
- Section detection: navbar, hero, form, cards, sidebar, footer
- Layout modes: vertical, horizontal, grid, absolute
- Style integration: colors, spacing, typography from style_analyzer

Author: Figma to Multicode Generator Team
Version: 2.0
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class NodeType(str, Enum):
    """Types of ILS nodes."""
    PAGE = "page"
    SECTION = "section"
    NAVBAR = "navbar"
    SIDEBAR = "sidebar"
    HERO = "hero"
    FORM = "form"
    CARDS = "cards"
    FOOTER = "footer"
    FRAME = "frame"
    TEXT_BLOCK = "text_block"
    HEADING = "heading"
    BUTTON = "button"
    INPUT_FIELD = "input_field"
    PASSWORD_INPUT = "password_input"
    IMAGE_BLOCK = "image_block"
    CARD = "card"
    LINK = "link"
    UNKNOWN = "unknown"


class LayoutMode(str, Enum):
    """Layout modes for containers."""
    VERTICAL = "vertical"      # flex-col
    HORIZONTAL = "horizontal"  # flex-row
    GRID = "grid"             # grid
    ABSOLUTE = "absolute"     # absolute positioning


class Role(str, Enum):
    """Semantic roles for elements."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    CTA = "cta"              # Call to action
    HIGHLIGHT = "highlight"
    NEUTRAL = "neutral"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ILSNode:
    """
    A node in the ILS tree representing a UI element or container.
    
    This is the core data structure for ILS v2. Each node can have:
    - Basic info: id, type, role
    - Geometry: rect (x, y, w, h)
    - Layout: how children are arranged
    - Style: colors, spacing, typography
    - Children: nested nodes
    """
    id: str
    type: NodeType
    role: Optional[Role] = None
    rect: Optional[Dict[str, int]] = None  # {"x": int, "y": int, "w": int, "h": int}
    
    # Layout configuration for containers
    layout: Dict[str, Any] = field(default_factory=lambda: {
        "mode": LayoutMode.VERTICAL,
        "columns": None,
        "gap": None,
        "padding": None,
        "align": None,        # start | center | end
        "justify": None,      # start | center | end | space-between
        "z_index": None
    })
    
    # Style configuration
    style: Dict[str, Any] = field(default_factory=lambda: {
        "background_color": None,
        "text_color": None,
        "primary_color": None,
        "accent_color": None,
        "border_radius": None,
        "font_scale": None,    # title | heading | body | caption
        "variant": None        # solid | outline | ghost
    })
    
    # Text content (if applicable)
    text: Optional[str] = None
    
    # Children nodes
    children: List["ILSNode"] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        result = {
            "id": self.id,
            "type": self.type.value if isinstance(self.type, Enum) else self.type,
        }
        
        if self.role:
            result["role"] = self.role.value if isinstance(self.role, Enum) else self.role
        
        if self.rect:
            result["rect"] = self.rect
        
        # Clean up layout (remove None values)
        clean_layout = {k: v for k, v in self.layout.items() if v is not None}
        if clean_layout:
            # Convert enums to strings
            if "mode" in clean_layout and isinstance(clean_layout["mode"], Enum):
                clean_layout["mode"] = clean_layout["mode"].value
            result["layout"] = clean_layout
        
        # Clean up style
        clean_style = {k: v for k, v in self.style.items() if v is not None}
        if clean_style:
            result["style"] = clean_style
        
        if self.text:
            result["text"] = self.text
        
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        
        return result


# ============================================================================
# SECTION DETECTION HELPERS
# ============================================================================

def detect_navbar(typed_blocks: List[Any], image_size: Tuple[int, int]) -> Optional[ILSNode]:
    """
    Detect navbar: horizontal section at top with full width.
    
    Args:
        typed_blocks: List of TypedBlock objects from classifier
        image_size: (height, width) of image
        
    Returns:
        ILSNode for navbar or None
    """
    image_h, image_w = image_size
    
    # Find blocks in top 15% of image that span most of width
    navbar_candidates = []
    for block in typed_blocks:
        y_pos = block.y
        width = block.w
        
        # Must be in top portion and span significant width
        if y_pos < image_h * 0.15 and width > image_w * 0.6:
            navbar_candidates.append(block)
    
    if not navbar_candidates:
        return None
    
    # Sort by y position and take topmost blocks
    navbar_candidates.sort(key=lambda b: b.y)
    navbar_blocks = []
    
    if navbar_candidates:
        first_y = navbar_candidates[0].y
        # Take all blocks within 50px of first block
        for block in navbar_candidates:
            if abs(block.y - first_y) < 50:
                navbar_blocks.append(block)
    
    if not navbar_blocks:
        return None
    
    # Calculate bounding box
    min_x = min(b.x for b in navbar_blocks)
    min_y = min(b.y for b in navbar_blocks)
    max_x = max(b.x + b.w for b in navbar_blocks)
    max_y = max(b.y + b.h for b in navbar_blocks)
    
    # Create navbar node
    navbar = ILSNode(
        id="navbar",
        type=NodeType.NAVBAR,
        rect={"x": min_x, "y": min_y, "w": max_x - min_x, "h": max_y - min_y},
        layout={
            "mode": LayoutMode.HORIZONTAL,
            "gap": 16,
            "padding": 16,
            "align": "center",
            "justify": "space-between"
        }
    )
    
    # Add children
    for block in navbar_blocks:
        child = create_leaf_node(block)
        navbar.children.append(child)
    
    logger.debug(f"Detected navbar with {len(navbar_blocks)} elements")
    return navbar


def detect_sidebar(typed_blocks: List[Any], image_size: Tuple[int, int]) -> Optional[ILSNode]:
    """
    Detect sidebar: narrow vertical column on left or right.
    
    Args:
        typed_blocks: List of TypedBlock objects
        image_size: (height, width) of image
        
    Returns:
        ILSNode for sidebar or None
    """
    image_h, image_w = image_size
    
    # Look for tall narrow columns on edges
    sidebar_candidates = []
    for block in typed_blocks:
        x_pos = block.x
        width = block.w
        height = block.h
        
        # Must be narrow (< 25% width) and tall (> 50% height)
        if width < image_w * 0.25 and height > image_h * 0.5:
            # On left or right edge
            if x_pos < image_w * 0.1 or x_pos > image_w * 0.75:
                sidebar_candidates.append(block)
    
    if not sidebar_candidates:
        return None
    
    # Take the tallest candidate
    sidebar_block = max(sidebar_candidates, key=lambda b: b.h)
    
    sidebar = ILSNode(
        id="sidebar",
        type=NodeType.SIDEBAR,
        rect={"x": sidebar_block.x, "y": sidebar_block.y, "w": sidebar_block.w, "h": sidebar_block.h},
        layout={
            "mode": LayoutMode.VERTICAL,
            "gap": 12,
            "padding": 16
        }
    )
    
    logger.debug(f"Detected sidebar at x={sidebar_block.x}")
    return sidebar


def detect_hero_section(typed_blocks: List[Any], image_size: Tuple[int, int]) -> Optional[ILSNode]:
    """
    Detect hero section: large image/heading near top-center.
    
    Args:
        typed_blocks: List of TypedBlock objects
        image_size: (height, width) of image
        
    Returns:
        ILSNode for hero or None
    """
    image_h, image_w = image_size
    
    # Look for large blocks in upper-middle portion
    hero_candidates = []
    for block in typed_blocks:
        y_pos = block.y
        x_pos = block.x
        width = block.w
        height = block.h
        area = width * height
        
        # In upper half, reasonably centered, large area
        if (0.1 * image_h < y_pos < 0.5 * image_h and
            0.2 * image_w < x_pos < 0.8 * image_w and
            area > image_w * image_h * 0.1):
            
            # Prefer headings and image blocks
            if block.type in ["heading", "image_block"]:
                hero_candidates.append(block)
    
    if not hero_candidates:
        return None
    
    # Take largest candidate
    hero_block = max(hero_candidates, key=lambda b: b.w * b.h)
    
    # Look for nearby blocks to include
    hero_blocks = [hero_block]
    hero_y_min = hero_block.y
    hero_y_max = hero_block.y + hero_block.h
    
    for block in typed_blocks:
        if block.id == hero_block.id:
            continue
        # Within vertical range
        if (hero_y_min - 100 < block.y < hero_y_max + 100 and
            0.2 * image_w < block.x < 0.8 * image_w):
            hero_blocks.append(block)
    
    # Calculate bounding box
    min_x = min(b.x for b in hero_blocks)
    min_y = min(b.y for b in hero_blocks)
    max_x = max(b.x + b.w for b in hero_blocks)
    max_y = max(b.y + b.h for b in hero_blocks)
    
    hero = ILSNode(
        id="hero",
        type=NodeType.HERO,
        role=Role.HIGHLIGHT,
        rect={"x": min_x, "y": min_y, "w": max_x - min_x, "h": max_y - min_y},
        layout={
            "mode": LayoutMode.VERTICAL,
            "gap": 24,
            "padding": 48,
            "align": "center"
        }
    )
    
    # Add children
    for block in hero_blocks:
        child = create_leaf_node(block)
        hero.children.append(child)
    
    logger.debug(f"Detected hero section with {len(hero_blocks)} elements")
    return hero


def detect_form_sections(typed_blocks: List[Any], image_size: Tuple[int, int]) -> List[ILSNode]:
    """
    Detect form sections: vertical groups of inputs + button.
    
    Args:
        typed_blocks: List of TypedBlock objects
        image_size: (height, width) of image
        
    Returns:
        List of ILSNode for forms
    """
    from .detection import cluster_rows
    
    # Find input fields and password inputs
    input_blocks = [b for b in typed_blocks if b.type in ["input_field", "password_input"]]
    
    if len(input_blocks) < 2:
        return []
    
    # Convert to dict format for clustering
    input_dicts = [{"x": b.x, "y": b.y, "w": b.w, "h": b.h, "block": b} for b in input_blocks]
    rows = cluster_rows(input_dicts, row_gap_threshold=30)
    
    # Look for vertical stacks of inputs
    forms = []
    for i, row_group in enumerate(rows):
        if len(row_group) >= 2:  # At least 2 inputs
            blocks_in_form = [item["block"] for item in row_group]
            
            # Look for nearby button
            form_y_min = min(b.y for b in blocks_in_form)
            form_y_max = max(b.y + b.h for b in blocks_in_form)
            form_x_center = np.mean([b.x + b.w / 2 for b in blocks_in_form])
            
            button_block = None
            for block in typed_blocks:
                if block.type == "button":
                    # Below the inputs, reasonably centered
                    if (form_y_max < block.y < form_y_max + 150 and
                        abs(block.x + block.w / 2 - form_x_center) < 200):
                        button_block = block
                        break
            
            if button_block:
                blocks_in_form.append(button_block)
            
            # Calculate bounding box
            min_x = min(b.x for b in blocks_in_form)
            min_y = min(b.y for b in blocks_in_form)
            max_x = max(b.x + b.w for b in blocks_in_form)
            max_y = max(b.y + b.h for b in blocks_in_form)
            
            form = ILSNode(
                id=f"form_{i+1}",
                type=NodeType.FORM,
                role=Role.PRIMARY,
                rect={"x": min_x, "y": min_y, "w": max_x - min_x, "h": max_y - min_y},
                layout={
                    "mode": LayoutMode.VERTICAL,
                    "gap": 16,
                    "padding": 24
                }
            )
            
            # Add children
            for block in blocks_in_form:
                child = create_leaf_node(block)
                if block.type == "button":
                    child.role = Role.PRIMARY
                form.children.append(child)
            
            forms.append(form)
            logger.debug(f"Detected form with {len(blocks_in_form)} elements")
    
    return forms


def detect_card_sections(typed_blocks: List[Any], image_size: Tuple[int, int]) -> List[ILSNode]:
    """
    Detect card grids: repeated card-like shapes.
    
    Args:
        typed_blocks: List of TypedBlock objects
        image_size: (height, width) of image
        
    Returns:
        List of ILSNode for card sections
    """
    # Find card-type blocks
    card_blocks = [b for b in typed_blocks if b.type == "card"]
    
    if len(card_blocks) < 2:
        return []
    
    # Group cards that are similar in size and aligned
    card_groups = []
    used = set()
    
    for i, card1 in enumerate(card_blocks):
        if i in used:
            continue
        
        group = [card1]
        used.add(i)
        
        for j, card2 in enumerate(card_blocks[i+1:], i+1):
            if j in used:
                continue
            
            # Similar size
            size_ratio = min(card1.w, card2.w) / max(card1.w, card2.w)
            height_ratio = min(card1.h, card2.h) / max(card1.h, card2.h)
            
            # Aligned vertically or horizontally
            h_aligned = abs(card1.y - card2.y) < 50
            v_aligned = abs(card1.x - card2.x) < 50
            
            if size_ratio > 0.7 and height_ratio > 0.7 and (h_aligned or v_aligned):
                group.append(card2)
                used.add(j)
        
        if len(group) >= 2:
            card_groups.append(group)
    
    # Create card section nodes
    sections = []
    for i, group in enumerate(card_groups):
        min_x = min(b.x for b in group)
        min_y = min(b.y for b in group)
        max_x = max(b.x + b.w for b in group)
        max_y = max(b.y + b.h for b in group)
        
        # Determine grid columns (estimate from layout)
        avg_card_w = np.mean([b.w for b in group])
        total_w = max_x - min_x
        columns = max(1, int(total_w / (avg_card_w * 1.2)))
        
        cards_section = ILSNode(
            id=f"cards_{i+1}",
            type=NodeType.CARDS,
            rect={"x": min_x, "y": min_y, "w": max_x - min_x, "h": max_y - min_y},
            layout={
                "mode": LayoutMode.GRID,
                "columns": columns,
                "gap": 24,
                "padding": 24
            }
        )
        
        # Add card children
        for block in group:
            card_node = create_leaf_node(block)
            cards_section.children.append(card_node)
        
        sections.append(cards_section)
        logger.debug(f"Detected card section with {len(group)} cards, {columns} columns")
    
    return sections


def detect_footer(typed_blocks: List[Any], image_size: Tuple[int, int]) -> Optional[ILSNode]:
    """
    Detect footer: horizontal section at bottom.
    
    Args:
        typed_blocks: List of TypedBlock objects
        image_size: (height, width) of image
        
    Returns:
        ILSNode for footer or None
    """
    image_h, image_w = image_size
    
    # Find blocks in bottom 15% of image
    footer_candidates = []
    for block in typed_blocks:
        y_pos = block.y
        
        # Must be in bottom portion
        if y_pos > image_h * 0.85:
            footer_candidates.append(block)
    
    if not footer_candidates:
        return None
    
    # Calculate bounding box
    min_x = min(b.x for b in footer_candidates)
    min_y = min(b.y for b in footer_candidates)
    max_x = max(b.x + b.w for b in footer_candidates)
    max_y = max(b.y + b.h for b in footer_candidates)
    
    footer = ILSNode(
        id="footer",
        type=NodeType.FOOTER,
        rect={"x": min_x, "y": min_y, "w": max_x - min_x, "h": max_y - min_y},
        layout={
            "mode": LayoutMode.HORIZONTAL,
            "gap": 16,
            "padding": 24,
            "justify": "center"
        }
    )
    
    # Add children
    for block in footer_candidates:
        child = create_leaf_node(block)
        footer.children.append(child)
    
    logger.debug(f"Detected footer with {len(footer_candidates)} elements")
    return footer


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_leaf_node(block: Any) -> ILSNode:
    """
    Create a leaf ILS node from a TypedBlock.
    
    Args:
        block: TypedBlock object from classifier
        
    Returns:
        ILSNode for the element
    """
    # Map type string to NodeType enum
    try:
        node_type = NodeType(block.type)
    except ValueError:
        node_type = NodeType.UNKNOWN
    
    return ILSNode(
        id=block.id,
        type=node_type,
        rect={"x": block.x, "y": block.y, "w": block.w, "h": block.h}
    )


def assign_used_blocks(sections: List[ILSNode]) -> set:
    """
    Get set of block IDs that are already used in sections.
    
    Args:
        sections: List of section nodes
        
    Returns:
        Set of block IDs
    """
    used = set()
    for section in sections:
        for child in section.children:
            used.add(child.id)
    return used


def create_generic_section(remaining_blocks: List[Any], section_id: str) -> ILSNode:
    """
    Create a generic section for remaining blocks.
    
    Args:
        remaining_blocks: List of TypedBlock objects
        section_id: ID for the section
        
    Returns:
        ILSNode for generic section
    """
    if not remaining_blocks:
        return None
    
    min_x = min(b.x for b in remaining_blocks)
    min_y = min(b.y for b in remaining_blocks)
    max_x = max(b.x + b.w for b in remaining_blocks)
    max_y = max(b.y + b.h for b in remaining_blocks)
    
    section = ILSNode(
        id=section_id,
        type=NodeType.SECTION,
        rect={"x": min_x, "y": min_y, "w": max_x - min_x, "h": max_y - min_y},
        layout={
            "mode": LayoutMode.VERTICAL,
            "gap": 16,
            "padding": 16
        }
    )
    
    # Add children
    for block in remaining_blocks:
        child = create_leaf_node(block)
        section.children.append(child)
    
    return section


# ============================================================================
# MAIN ILS BUILDER
# ============================================================================

def build_ils(typed_blocks: List[Any], style_info: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Build ILS v2 tree from classified blocks and style information.
    
    This is the main entry point for ILS construction. It:
    1. Detects semantic sections (navbar, hero, forms, cards, footer)
    2. Groups remaining blocks into generic sections
    3. Builds hierarchical tree structure
    4. Applies style information from style_analyzer
    5. Returns JSON-serializable dictionary
    
    Args:
        typed_blocks: List of TypedBlock objects from classifier
        style_info: Optional style analysis from style_analyzer
        
    Returns:
        Dictionary representation of ILS tree
        
    Examples:
        >>> typed_blocks = classify_blocks(model, image, blocks)
        >>> style_info = analyze_style(image, typed_blocks)
        >>> ils = build_ils(typed_blocks, style_info)
        >>> print(ils["type"])  # "page"
        >>> print(len(ils["children"]))  # Number of sections
    """
    if not typed_blocks:
        logger.warning("No blocks to build ILS from")
        return create_empty_page()
    
    # Get image dimensions from blocks
    image_h = max(b.y + b.h for b in typed_blocks)
    image_w = max(b.x + b.w for b in typed_blocks)
    image_size = (image_h, image_w)
    
    logger.info(f"Building ILS from {len(typed_blocks)} blocks")
    
    # ========================================================================
    # SECTION DETECTION
    # ========================================================================
    
    sections = []
    
    # 1. Navbar
    navbar = detect_navbar(typed_blocks, image_size)
    if navbar:
        sections.append(navbar)
    
    # 2. Sidebar
    sidebar = detect_sidebar(typed_blocks, image_size)
    if sidebar:
        sections.append(sidebar)
    
    # 3. Hero
    hero = detect_hero_section(typed_blocks, image_size)
    if hero:
        sections.append(hero)
    
    # 4. Forms
    forms = detect_form_sections(typed_blocks, image_size)
    sections.extend(forms)
    
    # 5. Cards
    card_sections = detect_card_sections(typed_blocks, image_size)
    sections.extend(card_sections)
    
    # 6. Footer
    footer = detect_footer(typed_blocks, image_size)
    if footer:
        sections.append(footer)
    
    # ========================================================================
    # HANDLE REMAINING BLOCKS
    # ========================================================================
    
    used_ids = assign_used_blocks(sections)
    remaining_blocks = [b for b in typed_blocks if b.id not in used_ids]
    
    if remaining_blocks:
        logger.debug(f"{len(remaining_blocks)} blocks not assigned to sections")
        # Group remaining blocks by vertical proximity
        from .detection import cluster_rows
        
        remaining_dicts = [{"x": b.x, "y": b.y, "w": b.w, "h": b.h, "block": b} for b in remaining_blocks]
        rows = cluster_rows(remaining_dicts, row_gap_threshold=50)
        
        for i, row in enumerate(rows):
            row_blocks = [item["block"] for item in row]
            section = create_generic_section(row_blocks, f"section_{i+1}")
            if section:
                sections.append(section)
    
    # Sort sections by vertical position
    sections.sort(key=lambda s: s.rect["y"] if s.rect else 0)
    
    # ========================================================================
    # BUILD PAGE NODE
    # ========================================================================
    
    page = ILSNode(
        id="page_root",
        type=NodeType.PAGE,
        layout={
            "mode": LayoutMode.VERTICAL,
            "gap": 0,
            "padding": 0
        },
        children=sections
    )
    
    # ========================================================================
    # APPLY STYLE INFORMATION
    # ========================================================================
    
    if style_info:
        apply_style_to_tree(page, style_info)
    
    logger.info(f"Built ILS tree with {len(sections)} sections")
    
    return page.to_dict()


def apply_style_to_tree(page: ILSNode, style_info: Dict) -> None:
    """
    Apply style information to ILS tree.
    
    Args:
        page: Root page node
        style_info: Style analysis from style_analyzer
    """
    # Apply page-level style
    if "page" in style_info:
        page_style = style_info["page"]
        page.style.update({
            "background_color": page_style.get("background_color"),
            "primary_color": page_style.get("primary_color"),
            "accent_color": page_style.get("accent_color"),
            "text_color": page_style.get("text_color")
        })
        
        # Update layout with base spacing
        if "base_spacing" in page_style:
            page.layout["gap"] = page_style["base_spacing"]
    
    # Apply block-level styles
    if "blocks" in style_info:
        block_styles = {b["id"]: b for b in style_info["blocks"]}
        
        def apply_to_node(node: ILSNode):
            if node.id in block_styles:
                block_style = block_styles[node.id]["style"]
                node.style.update({
                    "background_color": block_style.get("background_color"),
                    "text_color": block_style.get("text_color"),
                    "border_radius": block_style.get("border_radius"),
                    "font_scale": block_style.get("font_scale"),
                    "variant": block_style.get("variant")
                })
            
            for child in node.children:
                apply_to_node(child)
        
        for section in page.children:
            apply_to_node(section)


def create_empty_page() -> Dict[str, Any]:
    """Create an empty page structure."""
    page = ILSNode(
        id="page_root",
        type=NodeType.PAGE,
        layout={"mode": LayoutMode.VERTICAL}
    )
    return page.to_dict()

