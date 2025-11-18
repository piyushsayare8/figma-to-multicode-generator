"""
HTML + CSS Code Generator.

This module generates production-ready HTML code with vanilla CSS
from an Intermediate Layout Schema (ILS).
"""

import logging
from typing import Dict, Any, List
import os

from config import Config

logger = logging.getLogger(__name__)

class HtmlCssGenerator:
    """Generator for HTML + CSS code."""
    
    def __init__(self):
        self.config = Config()
        self.css_styles = []
        self.element_counter = 0
        
    def _generate_unique_id(self, prefix: str = "element") -> str:
        """Generate a unique ID for elements."""
        self.element_counter += 1
        return f"{prefix}_{self.element_counter}"
    
    def _add_css_rule(self, selector: str, styles: Dict[str, str]):
        """Add a CSS rule to the stylesheet."""
        style_declarations = []
        for property_name, value in styles.items():
            style_declarations.append(f"  {property_name}: {value};")
        
        rule = f"{selector} {{\n" + "\n".join(style_declarations) + "\n}"
        self.css_styles.append(rule)
    
    def generate_base_styles(self):
        """Generate base CSS styles."""
        # Reset and base styles
        self._add_css_rule("* ", {
            "margin": "0",
            "padding": "0",
            "box-sizing": "border-box"
        })
        
        self._add_css_rule("body", {
            "font-family": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
            "line-height": "1.6",
            "color": "#333",
            "background-color": "#f5f5f5",
            "min-height": "100vh",
            "padding": "20px"
        })
        
        # Container styles
        self._add_css_rule(".container", {
            "max-width": "1200px",
            "margin": "0 auto",
            "padding": "20px"
        })
        
        # Form styles
        self._add_css_rule(".form-container", {
            "max-width": "400px",
            "margin": "0 auto",
            "background": "white",
            "padding": "30px",
            "border-radius": "8px",
            "box-shadow": "0 2px 10px rgba(0,0,0,0.1)"
        })
        
        self._add_css_rule(".form-container h2", {
            "text-align": "center",
            "margin-bottom": "24px",
            "color": "#1f2937",
            "font-size": "24px",
            "font-weight": "bold"
        })
        
        self._add_css_rule(".form-group", {
            "margin-bottom": "20px"
        })
        
        self._add_css_rule(".form-group label", {
            "display": "block",
            "margin-bottom": "5px",
            "font-weight": "500",
            "color": "#374151",
            "font-size": "14px"
        })
        
        self._add_css_rule(".form-group input", {
            "width": "100%",
            "padding": "10px 12px",
            "border": "1px solid #d1d5db",
            "border-radius": "6px",
            "font-size": "16px",
            "transition": "border-color 0.2s"
        })
        
        self._add_css_rule(".form-group input:focus", {
            "outline": "none",
            "border-color": "#3b82f6",
            "box-shadow": "0 0 0 3px rgba(59, 130, 246, 0.1)"
        })
        
        self._add_css_rule(".form-group textarea", {
            "width": "100%",
            "padding": "10px 12px",
            "border": "1px solid #d1d5db",
            "border-radius": "6px",
            "font-size": "16px",
            "resize": "vertical",
            "min-height": "80px",
            "transition": "border-color 0.2s"
        })
        
        self._add_css_rule(".form-group textarea:focus", {
            "outline": "none",
            "border-color": "#3b82f6",
            "box-shadow": "0 0 0 3px rgba(59, 130, 246, 0.1)"
        })
        
        # Button styles
        self._add_css_rule(".btn-group", {
            "display": "flex",
            "gap": "10px",
            "margin-top": "24px"
        })
        
        self._add_css_rule(".btn", {
            "flex": "1",
            "padding": "12px 20px",
            "border": "none",
            "border-radius": "6px",
            "font-size": "16px",
            "font-weight": "500",
            "cursor": "pointer",
            "transition": "background-color 0.2s"
        })
        
        self._add_css_rule(".btn-primary", {
            "background-color": "#3b82f6",
            "color": "white"
        })
        
        self._add_css_rule(".btn-primary:hover", {
            "background-color": "#2563eb"
        })
        
        self._add_css_rule(".btn-secondary", {
            "background-color": "white",
            "color": "#374151",
            "border": "1px solid #d1d5db"
        })
        
        self._add_css_rule(".btn-secondary:hover", {
            "background-color": "#f9fafb"
        })
        
        # Cards styles
        self._add_css_rule(".cards-container", {
            "max-width": "1200px",
            "margin": "0 auto",
            "padding": "40px 20px"
        })
        
        self._add_css_rule(".cards-container h2", {
            "text-align": "center",
            "margin-bottom": "40px",
            "color": "#1f2937",
            "font-size": "32px",
            "font-weight": "bold"
        })
        
        self._add_css_rule(".cards-grid", {
            "display": "grid",
            "grid-template-columns": "repeat(auto-fit, minmax(300px, 1fr))",
            "gap": "24px"
        })
        
        self._add_css_rule(".card", {
            "background": "white",
            "padding": "24px",
            "border-radius": "8px",
            "box-shadow": "0 2px 8px rgba(0,0,0,0.1)",
            "transition": "box-shadow 0.2s"
        })
        
        self._add_css_rule(".card:hover", {
            "box-shadow": "0 4px 16px rgba(0,0,0,0.15)"
        })
        
        self._add_css_rule(".card h3", {
            "margin-bottom": "12px",
            "color": "#1f2937",
            "font-size": "20px",
            "font-weight": "600"
        })
        
        self._add_css_rule(".card p", {
            "color": "#6b7280",
            "line-height": "1.5"
        })
        
        # Content styles
        self._add_css_rule(".content-container", {
            "max-width": "800px",
            "margin": "0 auto",
            "padding": "40px 20px"
        })
        
        self._add_css_rule(".content-container h2", {
            "margin-bottom": "24px",
            "color": "#1f2937",
            "font-size": "32px",
            "font-weight": "bold"
        })
        
        self._add_css_rule(".content-section", {
            "margin-bottom": "24px"
        })
        
        self._add_css_rule(".content-text", {
            "color": "#374151",
            "line-height": "1.7",
            "font-size": "16px"
        })
        
        self._add_css_rule(".content-image", {
            "text-align": "center",
            "margin": "24px 0"
        })
        
        self._add_css_rule(".content-image img", {
            "max-width": "100%",
            "height": "auto",
            "border-radius": "8px",
            "box-shadow": "0 2px 8px rgba(0,0,0,0.1)"
        })
        
        # Text block styles
        self._add_css_rule(".text-block", {
            "margin-bottom": "16px",
            "color": "#6b7280",
            "font-size": "14px"
        })
    
    def generate_form_section(self, section: Dict[str, Any]) -> str:
        """Generate HTML for a form section."""
        elements = section.get('elements', [])
        primary_action = section.get('primary_action', {})
        secondary_actions = section.get('secondary_actions', [])
        title = section.get('title', 'Form')
        form_id = self._generate_unique_id("form")
        
        html_parts = []
        
        # Form container start
        html_parts.append(f'''
    <div class="form-container">
        <h2>{title}</h2>
        <form id="{form_id}">''')
        
        # Form elements
        for element in elements:
            element_html = self.generate_form_element(element)
            if element_html:
                html_parts.append(element_html)
        
        # Actions
        if primary_action or secondary_actions:
            html_parts.append('            <div class="btn-group">')
            
            # Secondary actions first
            for action in secondary_actions:
                html_parts.append(self.generate_button_element(action, secondary=True))
            
            # Primary action
            if primary_action:
                html_parts.append(self.generate_button_element(primary_action, secondary=False))
            
            html_parts.append('            </div>')
        
        # Form container end
        html_parts.append('''        </form>
    </div>''')
        
        return '\n'.join(html_parts)
    
    def generate_form_element(self, element: Dict[str, Any]) -> str:
        """Generate HTML for a single form element."""
        element_type = element.get('type', '')
        label = element.get('label', '')
        name = element.get('name', '')
        placeholder = element.get('placeholder', '')
        required = element.get('required', False)
        element_id = self._generate_unique_id("input")
        
        if element_type in ['text_input', 'email_input', 'password_input']:
            input_type = 'text'
            if element_type == 'password_input':
                input_type = 'password'
            elif element_type == 'email_input':
                input_type = 'email'
                
            return f'''            <div class="form-group">
                <label for="{element_id}">{label}</label>
                <input type="{input_type}" id="{element_id}" name="{name}" placeholder="{placeholder}"
                       {"required" if required else ""}>
            </div>'''
        
        elif element_type == 'textarea':
            return f'''            <div class="form-group">
                <label for="{element_id}">{label}</label>
                <textarea id="{element_id}" name="{name}" placeholder="{placeholder}"
                          {"required" if required else ""}></textarea>
            </div>'''
        
        elif element_type == 'text_block':
            return f'''            <div class="text-block">
                {label}
            </div>'''
        
        return ''
    
    def generate_button_element(self, button: Dict[str, Any], secondary: bool = False) -> str:
        """Generate HTML for a button element."""
        label = button.get('label', 'Button')
        button_id = self._generate_unique_id("btn")
        
        button_class = "btn btn-secondary" if secondary else "btn btn-primary"
        button_type = "button" if secondary else "submit"
        
        return f'''                <button type="{button_type}" id="{button_id}" class="{button_class}">
                    {label}
                </button>'''
    
    def generate_cards_section(self, section: Dict[str, Any]) -> str:
        """Generate HTML for a cards section."""
        elements = section.get('elements', [])
        title = section.get('title', 'Cards')
        
        html_parts = []
        
        # Cards container start
        html_parts.append(f'''
    <div class="cards-container">
        <h2>{title}</h2>
        <div class="cards-grid">''')
        
        # Cards
        for element in elements:
            if element.get('type') == 'card':
                card_html = self.generate_card_element(element)
                html_parts.append(card_html)
        
        # Cards container end
        html_parts.append('''        </div>
    </div>''')
        
        return '\n'.join(html_parts)
    
    def generate_card_element(self, element: Dict[str, Any]) -> str:
        """Generate HTML for a single card element."""
        label = element.get('label', 'Card')
        value = element.get('value', 'Card content goes here.')
        card_id = self._generate_unique_id("card")
        
        return f'''            <div class="card" id="{card_id}">
                <h3>{label}</h3>
                <p>{value}</p>
            </div>'''
    
    def generate_content_section(self, section: Dict[str, Any]) -> str:
        """Generate HTML for a content section."""
        elements = section.get('elements', [])
        title = section.get('title', 'Content')
        
        html_parts = []
        
        # Content container start
        html_parts.append(f'''
    <div class="content-container">
        <h2>{title}</h2>
        <div class="content-section">''')
        
        # Content elements
        for element in elements:
            element_html = self.generate_content_element(element)
            if element_html:
                html_parts.append(element_html)
        
        # Content container end
        html_parts.append('''        </div>
    </div>''')
        
        return '\n'.join(html_parts)
    
    def generate_content_element(self, element: Dict[str, Any]) -> str:
        """Generate HTML for a single content element."""
        element_type = element.get('type', '')
        label = element.get('label', '')
        value = element.get('value', '')
        element_id = self._generate_unique_id("content")
        
        if element_type == 'text_block':
            return f'''            <div class="content-text" id="{element_id}">
                {label}
            </div>'''
        
        elif element_type == 'image_block':
            return f'''            <div class="content-image" id="{element_id}">
                <img src="{value}" alt="{label}">
            </div>'''
        
        return ''
    
    def generate_page_structure(self, ils: Dict[str, Any]) -> str:
        """Generate the complete HTML page structure."""
        title = ils.get('title', 'Generated UI')
        sections = ils.get('sections', [])
        
        # Generate base CSS
        self.generate_base_styles()
        
        # Generate sections content
        sections_html = []
        for section in sections:
            section_type = section.get('type', '')
            
            if section_type == 'form':
                section_html = self.generate_form_section(section)
            elif section_type == 'cards':
                section_html = self.generate_cards_section(section)
            elif section_type == 'content':
                section_html = self.generate_content_section(section)
            else:
                # Default content section
                section_html = self.generate_content_section(section)
            
            sections_html.append(section_html)
        
        # Generate CSS
        css_content = '\n\n'.join(self.css_styles)
        
        # Complete page template
        page_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="container">
{''.join(sections_html)}
    </div>
</body>
</html>'''
        
        return page_template

def generate_html_css(ils: Dict[str, Any]) -> str:
    """
    Generate HTML + CSS code from an ILS.
    
    This is the main function called by the API endpoint.
    
    Args:
        ils: Intermediate Layout Schema dictionary
        
    Returns:
        Complete HTML page with vanilla CSS
    """
    logger.debug(f"Generating HTML+CSS code from ILS: {ils.get('title', 'Unknown')}")
    
    if not ils or not isinstance(ils, dict):
        logger.error("Invalid ILS provided for HTML+CSS generation")
        return '<!DOCTYPE html><html><head><title>Error</title></head><body><p>Invalid UI specification</p></body></html>'
    
    generator = HtmlCssGenerator()
    
    try:
        html_code = generator.generate_page_structure(ils)
        logger.info(f"Successfully generated HTML+CSS code ({len(html_code)} characters)")
        return html_code
        
    except Exception as e:
        logger.error(f"Error generating HTML+CSS code: {str(e)}")
        # Return error page
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generation Error</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .error {{ color: red; }}
    </style>
</head>
<body>
    <h1 class="error">Generation Error</h1>
    <p>Failed to generate code: {str(e)}</p>
</body>
</html>'''

# Backward compatibility aliases
generate_plain_html_and_css = lambda ils: (generate_html_css(ils), "")