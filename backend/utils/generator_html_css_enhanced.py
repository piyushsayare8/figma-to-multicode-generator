"""
HTML + CSS Code Generator - STYLE-AWARE UPGRADE.

Generates separate index.html and styles.css files with:
  - CSS variables for theme colors
  - Proper semantic classes (.card, .form-group, .btn-primary)
  - Responsive design
  - Form handling script
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


def generate_css(ils: Dict[str, Any]) -> str:
    """
    Generate CSS stylesheet from ILS with style awareness.
    
    Args:
        ils: Intermediate Layout Schema
        
    Returns:
        CSS content as string
    """
    page_style = ils.get('style', {})
    
    # Extract colors
    bg_color = page_style.get('background_color', '#f5f6fa')
    primary_color = page_style.get('primary_color', '#2563eb')
    accent_color = page_style.get('accent_color', '#f59e0b')
    text_color = page_style.get('text_color', '#111827')
    base_spacing = page_style.get('base_spacing', 16)
    
    css = f'''/* Generated Styles - Style-Aware */

:root {{
    --bg-color: {bg_color};
    --primary-color: {primary_color};
    --accent-color: {accent_color};
    --text-color: {text_color};
    --base-spacing: {base_spacing}px;
    
    --border-radius: 8px;
    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}}

/* Reset and base styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}}

.page-container {{
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
}}

/* Card styles */
.card {{
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-lg);
    padding: calc(var(--base-spacing) * 1.5);
    margin-bottom: calc(var(--base-spacing) * 1.5);
}}

/* Form styles */
.form-container {{
    max-width: 28rem;
    margin: 0 auto;
}}

.form-group {{
    margin-bottom: var(--base-spacing);
}}

.form-group label {{
    display: block;
    font-weight: 500;
    font-size: 0.875rem;
    color: #374151;
    margin-bottom: calc(var(--base-spacing) * 0.25);
}}

.form-group input,
.form-group textarea {{
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: var(--border-radius);
    font-size: 1rem;
    transition: all 0.2s;
}}

.form-group input:focus,
.form-group textarea:focus {{
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}}

.form-group textarea {{
    resize: vertical;
    min-height: 80px;
}}

/* Button styles */
.btn {{
    padding: 0.5rem 1rem;
    border-radius: var(--border-radius);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
    display: inline-block;
}}

.btn-primary {{
    background-color: var(--primary-color);
    color: white;
}}

.btn-primary:hover {{
    opacity: 0.9;
    transform: translateY(-1px);
    box-shadow: var(--shadow);
}}

.btn-secondary {{
    background-color: white;
    color: #374151;
    border: 1px solid #d1d5db;
}}

.btn-secondary:hover {{
    background-color: #f9fafb;
}}

.btn-group {{
    display: flex;
    gap: calc(var(--base-spacing) * 0.5);
    margin-top: calc(var(--base-spacing) * 1.5);
}}

.btn-group .btn {{
    flex: 1;
}}

/* Cards grid */
.cards-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--base-spacing);
    margin-bottom: calc(var(--base-spacing) * 2);
}}

.card-item {{
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    padding: var(--base-spacing);
    transition: all 0.3s;
}}

.card-item:hover {{
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}}

.card-title {{
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: calc(var(--base-spacing) * 0.5);
}}

.card-body {{
    color: #6b7280;
    font-size: 0.875rem;
}}

/* Content styles */
.content-section {{
    max-width: 48rem;
    margin: 0 auto;
}}

.content-section p {{
    margin-bottom: calc(var(--base-spacing) * 0.75);
    color: #4b5563;
}}

.content-section img {{
    width: 100%;
    height: auto;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    margin-bottom: var(--base-spacing);
}}

/* Utility classes */
.text-center {{
    text-align: center;
}}

.mb-1 {{ margin-bottom: calc(var(--base-spacing) * 0.5); }}
.mb-2 {{ margin-bottom: var(--base-spacing); }}
.mb-3 {{ margin-bottom: calc(var(--base-spacing) * 1.5); }}
.mb-4 {{ margin-bottom: calc(var(--base-spacing) * 2); }}

/* Responsive */
@media (max-width: 640px) {{
    body {{
        padding: 1rem;
    }}
    
    .card {{
        padding: var(--base-spacing);
    }}
    
    .cards-grid {{
        grid-template-columns: 1fr;
    }}
}}
'''
    
    return css


def generate_html_body(ils: Dict[str, Any]) -> str:
    """Generate HTML body content from ILS sections."""
    sections = ils.get('sections', [])
    html_parts = []
    
    for section in sections:
        section_type = section.get('type', 'content')
        
        if section_type == 'form':
            html_parts.append(generate_form_html(section))
        elif section_type == 'cards':
            html_parts.append(generate_cards_html(section))
        else:
            html_parts.append(generate_content_html(section))
    
    return '\n'.join(html_parts)


def generate_form_html(section: Dict[str, Any]) -> str:
    """Generate form HTML."""
    fields = section.get('fields', section.get('elements', []))
    primary_action = section.get('primary_action')
    secondary_actions = section.get('secondary_actions', [])
    
    html_parts = [
        '    <div class="form-container">',
        '        <div class="card">',
        '            <form onsubmit="handleFormSubmit(event)">'
    ]
    
    # Fields
    for field in fields:
        field_html = generate_field_html(field)
        if field_html:
            html_parts.append(field_html)
    
    # Actions
    if primary_action or secondary_actions:
        html_parts.append('                <div class="btn-group">')
        
        for action in secondary_actions:
            label = action.get('label', 'Cancel')
            html_parts.append(f'                    <button type="button" class="btn btn-secondary">{label}</button>')
        
        if primary_action:
            label = primary_action.get('label', 'Submit')
            html_parts.append(f'                    <button type="submit" class="btn btn-primary">{label}</button>')
        
        html_parts.append('                </div>')
    
    html_parts.extend([
        '            </form>',
        '        </div>',
        '    </div>'
    ])
    
    return '\n'.join(html_parts)


def generate_field_html(field: Dict[str, Any]) -> str:
    """Generate HTML for a form field."""
    field_type = field.get('type', 'text_input')
    label = field.get('label', '')
    name = field.get('name', 'field')
    placeholder = field.get('placeholder', '')
    required = field.get('required', False)
    
    required_attr = ' required' if required else ''
    
    if field_type in ['text_input', 'email_input']:
        input_type = 'email' if field_type == 'email_input' else 'text'
        return f'''                <div class="form-group">
                    <label for="{name}">{label}</label>
                    <input type="{input_type}" id="{name}" name="{name}" placeholder="{placeholder}"{required_attr}>
                </div>'''
    
    elif field_type == 'password_input':
        return f'''                <div class="form-group">
                    <label for="{name}">{label}</label>
                    <input type="password" id="{name}" name="{name}" placeholder="{placeholder}"{required_attr}>
                </div>'''
    
    elif field_type == 'textarea':
        return f'''                <div class="form-group">
                    <label for="{name}">{label}</label>
                    <textarea id="{name}" name="{name}" placeholder="{placeholder}"{required_attr}></textarea>
                </div>'''
    
    elif field_type == 'text_block':
        return f'                <p class="mb-2">{label}</p>'
    
    return ''


def generate_cards_html(section: Dict[str, Any]) -> str:
    """Generate cards grid HTML."""
    cards = section.get('cards', [])
    
    html_parts = [
        '    <div class="cards-grid">'
    ]
    
    for card in cards:
        title = card.get('title', 'Card')
        body = card.get('body', 'Card content.')
        
        html_parts.append(f'''        <div class="card-item">
            <h3 class="card-title">{title}</h3>
            <p class="card-body">{body}</p>
        </div>''')
    
    html_parts.append('    </div>')
    
    return '\n'.join(html_parts)


def generate_content_html(section: Dict[str, Any]) -> str:
    """Generate content section HTML."""
    elements = section.get('elements', [])
    
    html_parts = [
        '    <div class="content-section">'
    ]
    
    for element in elements:
        element_type = element.get('type', '')
        label = element.get('label', '')
        value = element.get('value', '')
        
        if element_type == 'text_block':
            html_parts.append(f'        <p>{label}</p>')
        elif element_type == 'image_block':
            html_parts.append(f'        <img src="{value}" alt="{label}">')
    
    html_parts.append('    </div>')
    
    return '\n'.join(html_parts)


def generate_plain_html_and_css(ils: Dict[str, Any]) -> Tuple[str, str]:
    """
    Generate complete HTML and CSS from ILS.
    
    Args:
        ils: Intermediate Layout Schema
        
    Returns:
        Tuple of (html_content, css_content)
    """
    logger.info("Generating plain HTML and CSS from ILS")
    
    title = ils.get('title', 'Generated UI')
    body_html = generate_html_body(ils)
    css_content = generate_css(ils)
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="page-container">
{body_html}
    </div>
    
    <script>
        function handleFormSubmit(event) {{
            event.preventDefault();
            const formData = new FormData(event.target);
            const data = Object.fromEntries(formData.entries());
            console.log('Form submitted:', data);
            alert('Form submitted successfully! Check console for data.');
        }}
    </script>
</body>
</html>'''
    
    logger.info("Generated plain HTML and CSS")
    return html_content, css_content
