"""
Tailwind CSS Code Generator for ILS v2

Generates complete HTML with Tailwind CSS from ILS tree structure.
Walks the tree recursively and maps layout/style to Tailwind classes.

Author: Figma to Multicode Generator Team
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# TAILWIND CLASS MAPPING
# ============================================================================

def map_layout_mode_to_flex(mode: str) -> str:
    """Map ILS layout mode to Tailwind flex classes."""
    mapping = {
        "vertical": "flex flex-col",
        "horizontal": "flex flex-row",
        "grid": "grid",
        "absolute": "relative"
    }
    return mapping.get(mode, "flex flex-col")


def map_gap_to_tailwind(gap: Optional[int]) -> str:
    """Map gap pixels to Tailwind gap class."""
    if gap is None:
        return ""
    
    # Tailwind scale: gap-0, gap-1 (4px), gap-2 (8px), gap-4 (16px), gap-6 (24px), gap-8 (32px)
    if gap <= 2:
        return "gap-0"
    elif gap <= 6:
        return "gap-1"
    elif gap <= 12:
        return "gap-2"
    elif gap <= 20:
        return "gap-4"
    elif gap <= 28:
        return "gap-6"
    else:
        return "gap-8"


def map_padding_to_tailwind(padding: Optional[int]) -> str:
    """Map padding pixels to Tailwind padding class."""
    if padding is None:
        return ""
    
    if padding <= 2:
        return "p-0"
    elif padding <= 6:
        return "p-1"
    elif padding <= 12:
        return "p-2"
    elif padding <= 20:
        return "p-4"
    elif padding <= 28:
        return "p-6"
    elif padding <= 40:
        return "p-8"
    else:
        return "p-12"


def map_border_radius_to_tailwind(radius: Optional[int]) -> str:
    """Map border radius pixels to Tailwind rounded class."""
    if radius is None:
        return ""
    
    if radius <= 0:
        return "rounded-none"
    elif radius <= 4:
        return "rounded"
    elif radius <= 8:
        return "rounded-md"
    elif radius <= 12:
        return "rounded-lg"
    elif radius <= 24:
        return "rounded-xl"
    else:
        return "rounded-full"


def map_align_to_tailwind(align: Optional[str]) -> str:
    """Map alignment to Tailwind items class."""
    if not align:
        return ""
    
    mapping = {
        "start": "items-start",
        "center": "items-center",
        "end": "items-end"
    }
    return mapping.get(align, "")


def map_justify_to_tailwind(justify: Optional[str]) -> str:
    """Map justify to Tailwind justify class."""
    if not justify:
        return ""
    
    mapping = {
        "start": "justify-start",
        "center": "justify-center",
        "end": "justify-end",
        "space-between": "justify-between"
    }
    return mapping.get(justify, "")


def map_font_scale_to_tailwind(font_scale: Optional[str]) -> str:
    """Map font scale to Tailwind text size class."""
    if not font_scale:
        return "text-base"
    
    mapping = {
        "title": "text-4xl font-bold",
        "heading": "text-2xl font-semibold",
        "body": "text-base",
        "caption": "text-sm text-gray-600"
    }
    return mapping.get(font_scale, "text-base")


def color_to_tailwind_style(color: Optional[str], property: str) -> str:
    """
    Convert hex color to inline style for Tailwind.
    
    Args:
        color: Hex color like "#2563eb"
        property: CSS property like "background-color" or "color"
        
    Returns:
        Inline style string
    """
    if not color:
        return ""
    
    return f"{property}: {color};"


# ============================================================================
# NODE RENDERING
# ============================================================================

def render_node(node: Dict[str, Any], depth: int = 0) -> str:
    """
    Recursively render an ILS node to Tailwind HTML.
    
    Args:
        node: ILS node dictionary
        depth: Current nesting depth (for indentation)
        
    Returns:
        HTML string
    """
    indent = "  " * depth
    node_type = node.get("type", "unknown")
    
    # Route to appropriate renderer
    if node_type == "page":
        return render_page(node, depth)
    elif node_type in ["navbar", "hero", "form", "cards", "footer", "section", "sidebar"]:
        return render_section(node, depth)
    elif node_type == "button":
        return render_button(node, depth)
    elif node_type in ["input_field", "password_input"]:
        return render_input(node, depth)
    elif node_type in ["heading", "text_block"]:
        return render_text(node, depth)
    elif node_type == "image_block":
        return render_image(node, depth)
    elif node_type == "card":
        return render_card(node, depth)
    elif node_type == "link":
        return render_link(node, depth)
    else:
        return render_generic(node, depth)


def render_page(node: Dict[str, Any], depth: int) -> str:
    """Render page root node."""
    indent = "  " * depth
    
    # Extract styles
    style_obj = node.get("style", {})
    bg_color = style_obj.get("background_color", "#ffffff")
    text_color = style_obj.get("text_color", "#111827")
    
    # Build classes
    layout = node.get("layout", {})
    mode = layout.get("mode", "vertical")
    gap = layout.get("gap", 0)
    
    classes = [
        "min-h-screen",
        map_layout_mode_to_flex(mode),
        map_gap_to_tailwind(gap)
    ]
    
    classes_str = " ".join(filter(None, classes))
    
    # Build inline styles
    inline_styles = []
    inline_styles.append(color_to_tailwind_style(bg_color, "background-color"))
    inline_styles.append(color_to_tailwind_style(text_color, "color"))
    style_str = " ".join(filter(None, inline_styles))
    
    # Render children
    children_html = ""
    for child in node.get("children", []):
        children_html += render_node(child, depth + 1)
    
    return f"""{indent}<div class="{classes_str}" style="{style_str}">
{children_html}{indent}</div>"""


def render_section(node: Dict[str, Any], depth: int) -> str:
    """Render section container (navbar, hero, form, cards, etc.)."""
    indent = "  " * depth
    node_type = node.get("type", "section")
    
    # Extract layout
    layout = node.get("layout", {})
    mode = layout.get("mode", "vertical")
    gap = layout.get("gap")
    padding = layout.get("padding")
    align = layout.get("align")
    justify = layout.get("justify")
    columns = layout.get("columns")
    
    # Build classes
    classes = [map_layout_mode_to_flex(mode)]
    
    if gap:
        classes.append(map_gap_to_tailwind(gap))
    
    if padding:
        classes.append(map_padding_to_tailwind(padding))
    
    if align:
        classes.append(map_align_to_tailwind(align))
    
    if justify:
        classes.append(map_justify_to_tailwind(justify))
    
    # Grid-specific
    if mode == "grid" and columns:
        classes.append(f"grid-cols-{columns}")
    
    # Type-specific classes
    if node_type == "navbar":
        classes.extend(["w-full", "shadow-sm"])
    elif node_type == "hero":
        classes.extend(["w-full", "text-center"])
    elif node_type == "form":
        classes.extend(["max-w-md", "mx-auto", "bg-white", "shadow-md", "rounded-lg"])
    elif node_type == "cards":
        classes.extend(["w-full"])
    elif node_type == "footer":
        classes.extend(["w-full", "mt-auto", "border-t"])
    
    classes_str = " ".join(filter(None, classes))
    
    # Extract styles
    style_obj = node.get("style", {})
    bg_color = style_obj.get("background_color")
    text_color = style_obj.get("text_color")
    border_radius = style_obj.get("border_radius")
    
    inline_styles = []
    if bg_color:
        inline_styles.append(color_to_tailwind_style(bg_color, "background-color"))
    if text_color:
        inline_styles.append(color_to_tailwind_style(text_color, "color"))
    
    style_str = " ".join(filter(None, inline_styles))
    
    # Add border radius to classes if present
    if border_radius:
        classes_str += " " + map_border_radius_to_tailwind(border_radius)
    
    # Render children
    children_html = ""
    for child in node.get("children", []):
        children_html += render_node(child, depth + 1)
    
    # Choose semantic tag
    tag = "section" if node_type in ["hero", "cards"] else "div"
    if node_type == "navbar":
        tag = "nav"
    elif node_type == "footer":
        tag = "footer"
    elif node_type == "form":
        tag = "form"
    
    if tag == "form":
        return f"""{indent}<{tag} class="{classes_str}" style="{style_str}" onsubmit="event.preventDefault(); alert('Form submitted!');">
{children_html}{indent}</{tag}>"""
    else:
        return f"""{indent}<{tag} class="{classes_str}" style="{style_str}">
{children_html}{indent}</{tag}>"""


def render_button(node: Dict[str, Any], depth: int) -> str:
    """Render button element."""
    indent = "  " * depth
    
    # Extract styles
    style_obj = node.get("style", {})
    bg_color = style_obj.get("background_color", "#2563eb")
    text_color = style_obj.get("text_color", "#ffffff")
    border_radius = style_obj.get("border_radius")
    variant = style_obj.get("variant", "solid")
    
    # Build classes
    classes = ["px-6", "py-2", "font-medium", "transition-colors"]
    
    if variant == "outline":
        classes.extend(["border-2", "bg-transparent", "hover:bg-opacity-10"])
    elif variant == "ghost":
        classes.extend(["bg-transparent", "hover:bg-opacity-10"])
    else:  # solid
        classes.extend(["hover:opacity-90"])
    
    if border_radius:
        classes.append(map_border_radius_to_tailwind(border_radius))
    else:
        classes.append("rounded-lg")
    
    classes_str = " ".join(classes)
    
    # Inline styles
    inline_styles = []
    if variant == "solid":
        inline_styles.append(color_to_tailwind_style(bg_color, "background-color"))
        inline_styles.append(color_to_tailwind_style(text_color, "color"))
    elif variant == "outline":
        inline_styles.append(color_to_tailwind_style(bg_color, "border-color"))
        inline_styles.append(color_to_tailwind_style(bg_color, "color"))
    
    style_str = " ".join(filter(None, inline_styles))
    
    text = node.get("text", "Button")
    role = node.get("role", "")
    
    button_type = "submit" if role == "primary" else "button"
    
    return f'{indent}<button type="{button_type}" class="{classes_str}" style="{style_str}">{text}</button>\n'


def render_input(node: Dict[str, Any], depth: int) -> str:
    """Render input field."""
    indent = "  " * depth
    node_type = node.get("type", "input_field")
    
    # Build classes
    classes = ["w-full", "px-4", "py-2", "border", "rounded-lg", "focus:outline-none", "focus:ring-2", "focus:ring-blue-500"]
    classes_str = " ".join(classes)
    
    # Determine input type
    input_type = "password" if node_type == "password_input" else "text"
    placeholder = "Password" if node_type == "password_input" else "Enter text"
    
    return f'{indent}<input type="{input_type}" class="{classes_str}" placeholder="{placeholder}" />\n'


def render_text(node: Dict[str, Any], depth: int) -> str:
    """Render text or heading element."""
    indent = "  " * depth
    node_type = node.get("type", "text_block")
    
    # Extract styles
    style_obj = node.get("style", {})
    text_color = style_obj.get("text_color")
    font_scale = style_obj.get("font_scale", "body")
    
    # Build classes
    classes = [map_font_scale_to_tailwind(font_scale)]
    classes_str = " ".join(filter(None, classes))
    
    # Inline styles
    inline_styles = []
    if text_color:
        inline_styles.append(color_to_tailwind_style(text_color, "color"))
    style_str = " ".join(filter(None, inline_styles))
    
    text = node.get("text", "Sample text")
    
    # Choose tag
    tag = "h1" if node_type == "heading" else "p"
    
    return f'{indent}<{tag} class="{classes_str}" style="{style_str}">{text}</{tag}>\n'


def render_image(node: Dict[str, Any], depth: int) -> str:
    """Render image placeholder."""
    indent = "  " * depth
    
    # Build classes
    classes = ["w-full", "h-48", "bg-gray-200", "rounded-lg", "flex", "items-center", "justify-center"]
    classes_str = " ".join(classes)
    
    return f'{indent}<div class="{classes_str}"><span class="text-gray-500">Image</span></div>\n'


def render_card(node: Dict[str, Any], depth: int) -> str:
    """Render card element."""
    indent = "  " * depth
    
    # Extract styles
    style_obj = node.get("style", {})
    bg_color = style_obj.get("background_color", "#ffffff")
    border_radius = style_obj.get("border_radius")
    
    # Build classes
    classes = ["p-6", "bg-white", "shadow-md", "hover:shadow-lg", "transition-shadow"]
    
    if border_radius:
        classes.append(map_border_radius_to_tailwind(border_radius))
    else:
        classes.append("rounded-lg")
    
    classes_str = " ".join(classes)
    
    # Inline styles
    inline_styles = []
    if bg_color != "#ffffff":
        inline_styles.append(color_to_tailwind_style(bg_color, "background-color"))
    style_str = " ".join(filter(None, inline_styles))
    
    # Render children or placeholder
    children = node.get("children", [])
    if children:
        children_html = ""
        for child in children:
            children_html += render_node(child, depth + 1)
        return f"""{indent}<div class="{classes_str}" style="{style_str}">
{children_html}{indent}</div>"""
    else:
        return f'{indent}<div class="{classes_str}" style="{style_str}"><p class="text-gray-600">Card content</p></div>\n'


def render_link(node: Dict[str, Any], depth: int) -> str:
    """Render link element."""
    indent = "  " * depth
    
    # Extract styles
    style_obj = node.get("style", {})
    text_color = style_obj.get("text_color", "#2563eb")
    
    classes = ["hover:underline"]
    classes_str = " ".join(classes)
    
    inline_styles = [color_to_tailwind_style(text_color, "color")]
    style_str = " ".join(filter(None, inline_styles))
    
    text = node.get("text", "Link")
    
    return f'{indent}<a href="#" class="{classes_str}" style="{style_str}">{text}</a>\n'


def render_generic(node: Dict[str, Any], depth: int) -> str:
    """Render unknown/generic node."""
    indent = "  " * depth
    
    classes = ["p-2"]
    classes_str = " ".join(classes)
    
    # Render children if present
    children = node.get("children", [])
    if children:
        children_html = ""
        for child in children:
            children_html += render_node(child, depth + 1)
        return f"""{indent}<div class="{classes_str}">
{children_html}{indent}</div>"""
    else:
        return f'{indent}<div class="{classes_str}">Element</div>\n'


# ============================================================================
# MAIN GENERATOR FUNCTION
# ============================================================================

def generate_tailwind_code(ils: Dict[str, Any]) -> str:
    """
    Generate complete HTML with Tailwind CSS from ILS tree.
    
    Args:
        ils: ILS dictionary (output from ils_builder.build_ils)
        
    Returns:
        Complete HTML string with Tailwind CDN
        
    Examples:
        >>> ils = build_ils(typed_blocks, style_info)
        >>> html = generate_tailwind_code(ils)
        >>> with open("output.html", "w") as f:
        >>>     f.write(html)
    """
    logger.info("Generating Tailwind HTML from ILS tree")
    
    # Render body content from ILS tree
    body_content = render_node(ils, depth=2)
    
    # Complete HTML document
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Generated UI</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
{body_content}
</body>
</html>"""
    
    logger.info("Tailwind HTML generation complete")
    return html
