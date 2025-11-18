"""
HTML + Tailwind CSS Code Generator - STYLE-AWARE UPGRADE.

This module generates production-ready HTML code with Tailwind CSS classes
from an Intermediate Layout Schema (ILS) with full style awareness.

Features:
  - Uses ILS page-level colors (background, primary, accent, text)
  - Applies section-level style (padding, gap, border-radius, alignment)
  - Generates complete <!doctype html> with responsive layout
  - Includes preventDefault form handling script
  - Shadow, rounded corners, and proper spacing
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_style_value(ils: Dict[str, Any], key: str, default: Any) -> Any:
    """Safely extract style value from ILS."""
    if 'style' in ils and key in ils['style']:
        return ils['style'][key]
    return default


def px_to_tailwind_spacing(px_value: int) -> str:
    """Convert pixel value to Tailwind spacing class."""
    # Tailwind uses 0.25rem (4px) units
    # p-4 = 16px, p-6 = 24px, p-8 = 32px
    if px_value <= 8:
        return "2"
    elif px_value <= 12:
        return "3"
    elif px_value <= 16:
        return "4"
    elif px_value <= 20:
        return "5"
    elif px_value <= 24:
        return "6"
    elif px_value <= 32:
        return "8"
    elif px_value <= 40:
        return "10"
    elif px_value <= 48:
        return "12"
    else:
        return "16"


def border_radius_to_tailwind(radius: int) -> str:
    """Convert border radius to Tailwind class."""
    if radius <= 0:
        return "rounded-none"
    elif radius <= 6:
        return "rounded"
    elif radius <= 12:
        return "rounded-lg"
    elif radius <= 20:
        return "rounded-xl"
    elif radius <= 32:
        return "rounded-2xl"
    else:
        return "rounded-full"


def alignment_to_tailwind(alignment: str) -> str:
    """Convert alignment to Tailwind classes."""
    if alignment == "center":
        return "items-center justify-center"
    elif alignment == "right":
        return "items-end justify-end"
    else:  # left or default
        return "items-start justify-start"


# ============================================================================
# SECTION GENERATORS
# ============================================================================

def generate_form_section(section: Dict[str, Any], page_style: Dict[str, Any]) -> str:
    """Generate HTML for a form section with style."""
    fields = section.get('fields', section.get('elements', []))
    primary_action = section.get('primary_action')
    secondary_actions = section.get('secondary_actions', [])
    section_style = section.get('style', {})
    
    # Extract style values
    primary_color = page_style.get('primary_color', '#2563eb')
    text_color = page_style.get('text_color', '#111827')
    
    padding = section_style.get('padding', 24)
    gap = section_style.get('gap', 16)
    border_radius = section_style.get('border_radius', 16)
    alignment = section_style.get('alignment', 'center')
    is_card = section_style.get('card', True)
    
    # Tailwind classes
    padding_class = f"p-{px_to_tailwind_spacing(padding)}"
    gap_class = f"space-y-{px_to_tailwind_spacing(gap)}"
    radius_class = border_radius_to_tailwind(border_radius)
    
    # Build form HTML
    card_classes = "bg-white shadow-lg" if is_card else "bg-transparent"
    
    html_parts = [
        f'        <div class="max-w-md mx-auto {card_classes} {radius_class} {padding_class}">',
        f'            <form class="{gap_class}" onsubmit="handleFormSubmit(event)">'
    ]
    
    # Form fields
    for field in fields:
        field_html = generate_form_field(field, primary_color, gap)
        if field_html:
            html_parts.append(field_html)
    
    # Actions
    if primary_action or secondary_actions:
        action_gap = f"space-x-{px_to_tailwind_spacing(gap // 2)}"
        html_parts.append(f'                <div class="flex {action_gap} pt-{px_to_tailwind_spacing(gap)}">')
        
        for action in secondary_actions:
            html_parts.append(generate_button(action, primary_color, secondary=True))
        
        if primary_action:
            html_parts.append(generate_button(primary_action, primary_color, secondary=False))
        
        html_parts.append('                </div>')
    
    html_parts.append('            </form>')
    html_parts.append('        </div>')
    
    return '\n'.join(html_parts)


def generate_form_field(field: Dict[str, Any], primary_color: str, gap: int) -> str:
    """Generate HTML for a single form field."""
    field_type = field.get('type', 'text_input')
    label = field.get('label', '')
    name = field.get('name', 'field')
    placeholder = field.get('placeholder', '')
    required = field.get('required', False)
    
    gap_class = f"mb-{px_to_tailwind_spacing(gap // 4)}"
    
    input_classes = "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary-color)] focus:border-transparent"
    
    if field_type in ['text_input', 'email_input']:
        input_type = 'email' if field_type == 'email_input' else 'text'
        return f'''                <div>
                    <label for="{name}" class="block text-sm font-medium text-gray-700 {gap_class}">{label}</label>
                    <input type="{input_type}" id="{name}" name="{name}" placeholder="{placeholder}"
                           class="{input_classes}"
                           {"required" if required else ""}>
                </div>'''
    
    elif field_type == 'password_input':
        return f'''                <div>
                    <label for="{name}" class="block text-sm font-medium text-gray-700 {gap_class}">{label}</label>
                    <input type="password" id="{name}" name="{name}" placeholder="{placeholder}"
                           class="{input_classes}"
                           {"required" if required else ""}>
                </div>'''
    
    elif field_type == 'textarea':
        return f'''                <div>
                    <label for="{name}" class="block text-sm font-medium text-gray-700 {gap_class}">{label}</label>
                    <textarea id="{name}" name="{name}" placeholder="{placeholder}" rows="3"
                              class="{input_classes}"
                              {"required" if required else ""}></textarea>
                </div>'''
    
    elif field_type == 'text_block':
        return f'''                <div class="text-sm text-gray-600">
                    {label}
                </div>'''
    
    return ''


def generate_button(button: Dict[str, Any], primary_color: str, secondary: bool = False) -> str:
    """Generate HTML for a button."""
    label = button.get('label', 'Button')
    
    if secondary:
        return f'''                    <button type="button"
                           class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--primary-color)] transition-colors">
                        {label}
                    </button>'''
    else:
        return f'''                    <button type="submit"
                           class="flex-1 px-4 py-2 text-sm font-medium text-white bg-[var(--primary-color)] border border-transparent rounded-lg hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--primary-color)] transition-all">
                        {label}
                    </button>'''


def generate_cards_section(section: Dict[str, Any], page_style: Dict[str, Any]) -> str:
    """Generate HTML for a cards section with style."""
    cards = section.get('cards', [])
    section_style = section.get('style', {})
    
    # Extract style
    padding = section_style.get('padding', 16)
    gap = section_style.get('gap', 16)
    border_radius = section_style.get('border_radius', 12)
    columns = section_style.get('columns', 3)
    
    # Tailwind classes
    padding_class = f"p-{px_to_tailwind_spacing(padding)}"
    gap_class = f"gap-{px_to_tailwind_spacing(gap)}"
    radius_class = border_radius_to_tailwind(border_radius)
    
    # Grid columns
    if columns == 1:
        grid_cols = "grid-cols-1"
    elif columns == 2:
        grid_cols = "grid-cols-1 md:grid-cols-2"
    elif columns == 3:
        grid_cols = "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
    else:
        grid_cols = f"grid-cols-1 md:grid-cols-2 lg:grid-cols-{min(columns, 4)}"
    
    html_parts = [
        f'        <div class="max-w-6xl mx-auto px-4 py-8">',
        f'            <div class="grid {grid_cols} {gap_class}">'
    ]
    
    for card in cards:
        card_html = generate_card(card, border_radius, padding)
        html_parts.append(card_html)
    
    html_parts.append('            </div>')
    html_parts.append('        </div>')
    
    return '\n'.join(html_parts)


def generate_card(card: Dict[str, Any], border_radius: int, padding: int) -> str:
    """Generate HTML for a single card."""
    title = card.get('title', 'Card')
    body = card.get('body', 'Card content.')
    
    radius_class = border_radius_to_tailwind(border_radius)
    padding_class = f"p-{px_to_tailwind_spacing(padding)}"
    
    return f'''                <div class="bg-white {radius_class} shadow-md {padding_class} hover:shadow-lg transition-shadow duration-200">
                    <h3 class="text-xl font-semibold text-gray-900 mb-3">{title}</h3>
                    <p class="text-gray-600">{body}</p>
                </div>'''


def generate_content_section(section: Dict[str, Any], page_style: Dict[str, Any]) -> str:
    """Generate HTML for a content section with style."""
    elements = section.get('elements', [])
    section_style = section.get('style', {})
    
    padding = section_style.get('padding', 16)
    gap = section_style.get('gap', 12)
    
    padding_class = f"p-{px_to_tailwind_spacing(padding)}"
    gap_class = f"space-y-{px_to_tailwind_spacing(gap)}"
    
    html_parts = [
        f'        <div class="max-w-4xl mx-auto px-4 py-8">',
        f'            <div class="{gap_class}">'
    ]
    
    for element in elements:
        element_html = generate_content_element(element)
        if element_html:
            html_parts.append(element_html)
    
    html_parts.append('            </div>')
    html_parts.append('        </div>')
    
    return '\n'.join(html_parts)


def generate_content_element(element: Dict[str, Any]) -> str:
    """Generate HTML for a content element."""
    element_type = element.get('type', '')
    label = element.get('label', '')
    value = element.get('value', '')
    
    if element_type == 'text_block':
        return f'                <p class="text-gray-700">{label}</p>'
    elif element_type == 'image_block':
        return f'                <img src="{value}" alt="{label}" class="w-full h-auto rounded-lg shadow-md">'
    
    return ''


# ============================================================================
# MAIN GENERATOR
# ============================================================================

def generate_tailwind_html(ils: Dict[str, Any]) -> str:
    """
    Generate complete HTML with Tailwind CSS from ILS.
    
    Args:
        ils: Intermediate Layout Schema with style info
        
    Returns:
        Complete HTML document as string
    """
    logger.info("Generating Tailwind HTML from ILS")
    
    # Extract page-level info
    title = ils.get('title', 'Generated UI')
    layout_mode = ils.get('layout_mode', 'single_column')
    page_style = ils.get('style', {})
    sections = ils.get('sections', [])
    
    # Extract colors
    bg_color = page_style.get('background_color', '#f5f6fa')
    primary_color = page_style.get('primary_color', '#2563eb')
    accent_color = page_style.get('accent_color', '#f59e0b')
    text_color = page_style.get('text_color', '#111827')
    
    # Build HTML structure
    html_parts = [
        '<!doctype html>',
        '<html lang="en" class="h-full">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'    <title>{title}</title>',
        '    <script src="https://cdn.tailwindcss.com"></script>',
        '    <style>',
        '        :root {',
        f'            --bg-color: {bg_color};',
        f'            --primary-color: {primary_color};',
        f'            --accent-color: {accent_color};',
        f'            --text-color: {text_color};',
        '        }',
        '    </style>',
        '</head>',
        f'<body class="min-h-screen bg-[var(--bg-color)] text-[var(--text-color)] flex items-center justify-center">',
        '    <div class="w-full py-8">'
    ]
    
    # Generate sections
    for section in sections:
        section_type = section.get('type', 'content')
        
        if section_type == 'form':
            section_html = generate_form_section(section, page_style)
        elif section_type == 'cards':
            section_html = generate_cards_section(section, page_style)
        else:
            section_html = generate_content_section(section, page_style)
        
        html_parts.append(section_html)
    
    # Add form handling script
    html_parts.extend([
        '    </div>',
        '    <script>',
        '        function handleFormSubmit(event) {',
        '            event.preventDefault();',
        '            const formData = new FormData(event.target);',
        '            const data = Object.fromEntries(formData.entries());',
        '            console.log("Form submitted:", data);',
        '            alert("Form submitted successfully! Check console for data.");',
        '        }',
        '    </script>',
        '</body>',
        '</html>'
    ])
    
    logger.info(f"Generated Tailwind HTML with {len(sections)} sections")
    return '\n'.join(html_parts)


# Backward compatibility
class TailwindGenerator:
    """Wrapper class for backward compatibility."""
    
    def generate(self, ils: Dict[str, Any]) -> str:
        """Generate Tailwind HTML from ILS."""
        return generate_tailwind_html(ils)
