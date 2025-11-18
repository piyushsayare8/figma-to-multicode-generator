"""
HTML + Tailwind CSS Code Generator.

This module generates production-ready HTML code with Tailwind CSS classes
from an Intermediate Layout Schema (ILS).
"""

import logging
from typing import Dict, Any, List
from jinja2 import Template, Environment, FileSystemLoader, TemplateNotFound
import os
import json

from config import Config

logger = logging.getLogger(__name__)

class TailwindGenerator:
    """Generator for HTML + Tailwind CSS code."""
    
    def __init__(self):
        self.config = Config()
        self.template_env = self._setup_template_environment()
        
    def _setup_template_environment(self) -> Environment:
        """Set up Jinja2 template environment."""
        # Look for templates in a templates directory
        template_dirs = [
            os.path.join(os.path.dirname(__file__), '..', 'templates', 'tailwind'),
            os.path.join(os.path.dirname(__file__), 'templates', 'tailwind')
        ]
        
        # Use the first existing directory, or default to current directory
        template_dir = next((d for d in template_dirs if os.path.exists(d)), '.')
        
        env = Environment(loader=FileSystemLoader(template_dir))
        env.globals['enumerate'] = enumerate
        env.globals['len'] = len
        
        return env
    
    def generate_form_section(self, section: Dict[str, Any]) -> str:
        """Generate HTML for a form section."""
        elements = section.get('elements', [])
        primary_action = section.get('primary_action', {})
        secondary_actions = section.get('secondary_actions', [])
        title = section.get('title', 'Form')
        
        html_parts = []
        
        # Form header
        html_parts.append(f'''
        <div class="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">{title}</h2>
            <form class="space-y-4">''')
        
        # Form elements
        for element in elements:
            element_html = self.generate_form_element(element)
            if element_html:
                html_parts.append(element_html)
        
        # Actions
        if primary_action or secondary_actions:
            html_parts.append('                <div class="flex space-x-3 pt-4">')
            
            # Secondary actions first (usually Cancel)
            for action in secondary_actions:
                html_parts.append(self.generate_button_element(action, secondary=True))
            
            # Primary action last (usually Submit)
            if primary_action:
                html_parts.append(self.generate_button_element(primary_action, secondary=False))
            
            html_parts.append('                </div>')
        
        # Form footer
        html_parts.append('''            </form>
        </div>''')
        
        return '\n'.join(html_parts)
    
    def generate_form_element(self, element: Dict[str, Any]) -> str:
        """Generate HTML for a single form element."""
        element_type = element.get('type', '')
        label = element.get('label', '')
        name = element.get('name', '')
        placeholder = element.get('placeholder', '')
        required = element.get('required', False)
        
        if element_type == 'text_input':
            return f'''                <div>
                    <label for="{name}" class="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                    <input type="text" id="{name}" name="{name}" placeholder="{placeholder}"
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           {"required" if required else ""}>
                </div>'''
        
        elif element_type == 'password_input':
            return f'''                <div>
                    <label for="{name}" class="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                    <input type="password" id="{name}" name="{name}" placeholder="{placeholder}"
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           {"required" if required else ""}>
                </div>'''
        
        elif element_type == 'email_input':
            return f'''                <div>
                    <label for="{name}" class="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                    <input type="email" id="{name}" name="{name}" placeholder="{placeholder}"
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           {"required" if required else ""}>
                </div>'''
        
        elif element_type == 'textarea':
            return f'''                <div>
                    <label for="{name}" class="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                    <textarea id="{name}" name="{name}" placeholder="{placeholder}" rows="3"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              {"required" if required else ""}></textarea>
                </div>'''
        
        elif element_type == 'text_block':
            return f'''                <div class="text-sm text-gray-600">
                    {label}
                </div>'''
        
        return ''
    
    def generate_button_element(self, button: Dict[str, Any], secondary: bool = False) -> str:
        """Generate HTML for a button element."""
        label = button.get('label', 'Button')
        
        if secondary:
            return f'''                    <button type="button"
                           class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                        {label}
                    </button>'''
        else:
            return f'''                    <button type="submit"
                           class="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                        {label}
                    </button>'''
    
    def generate_cards_section(self, section: Dict[str, Any]) -> str:
        """Generate HTML for a cards section."""
        elements = section.get('elements', [])
        title = section.get('title', 'Cards')
        
        html_parts = []
        
        # Section header
        html_parts.append(f'''
        <div class="max-w-6xl mx-auto px-4 py-8">
            <h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">{title}</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">''')
        
        # Cards
        for element in elements:
            if element.get('type') == 'card':
                card_html = self.generate_card_element(element)
                html_parts.append(card_html)
        
        # Section footer
        html_parts.append('''            </div>
        </div>''')
        
        return '\n'.join(html_parts)
    
    def generate_card_element(self, element: Dict[str, Any]) -> str:
        """Generate HTML for a single card element."""
        label = element.get('label', 'Card')
        value = element.get('value', 'Card content goes here.')
        
        return f'''                <div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
                    <h3 class="text-xl font-semibold text-gray-900 mb-3">{label}</h3>
                    <p class="text-gray-600">{value}</p>
                </div>'''
    
    def generate_content_section(self, section: Dict[str, Any]) -> str:
        """Generate HTML for a content section."""
        elements = section.get('elements', [])
        title = section.get('title', 'Content')
        
        html_parts = []
        
        # Section header
        html_parts.append(f'''
        <div class="max-w-4xl mx-auto px-4 py-8">
            <h2 class="text-3xl font-bold text-gray-900 mb-6">{title}</h2>
            <div class="space-y-6">''')
        
        # Content elements
        for element in elements:
            element_html = self.generate_content_element(element)
            if element_html:
                html_parts.append(element_html)
        
        # Section footer
        html_parts.append('''            </div>
        </div>''')
        
        return '\n'.join(html_parts)
    
    def generate_content_element(self, element: Dict[str, Any]) -> str:
        """Generate HTML for a single content element."""
        element_type = element.get('type', '')
        label = element.get('label', '')
        value = element.get('value', '')
        
        if element_type == 'text_block':
            return f'''                <div class="prose max-w-none">
                    <p class="text-gray-700 leading-relaxed">{label}</p>
                </div>'''
        
        elif element_type == 'image_block':
            return f'''                <div class="flex justify-center">
                    <img src="{value}" alt="{label}" class="max-w-full h-auto rounded-lg shadow-md">
                </div>'''
        
        return ''
    
    def generate_page_structure(self, ils: Dict[str, Any]) -> str:
        """Generate the complete HTML page structure."""
        title = ils.get('title', 'Generated UI')
        sections = ils.get('sections', [])
        
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
        
        # Complete page template
        page_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="py-12">
{''.join(sections_html)}
    </div>
</body>
</html>'''
        
        return page_template

def generate_tailwind(ils: Dict[str, Any]) -> str:
    """
    Generate HTML + Tailwind CSS code from an ILS.
    
    This is the main function called by the API endpoint.
    
    Args:
        ils: Intermediate Layout Schema dictionary
        
    Returns:
        Complete HTML page with Tailwind CSS classes
    """
    logger.debug(f"Generating Tailwind code from ILS: {ils.get('title', 'Unknown')}")
    
    if not ils or not isinstance(ils, dict):
        logger.error("Invalid ILS provided for Tailwind generation")
        return '<!DOCTYPE html><html><head><title>Error</title></head><body><p>Invalid UI specification</p></body></html>'
    
    generator = TailwindGenerator()
    
    try:
        html_code = generator.generate_page_structure(ils)
        logger.info(f"Successfully generated Tailwind HTML code ({len(html_code)} characters)")
        return html_code
        
    except Exception as e:
        logger.error(f"Error generating Tailwind code: {str(e)}")
        # Return error page
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generation Error</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen flex items-center justify-center">
    <div class="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 class="text-2xl font-bold text-red-600 mb-4">Generation Error</h1>
        <p class="text-gray-700">Failed to generate code: {str(e)}</p>
    </div>
</body>
</html>'''

# Backward compatibility aliases
generate_tailwind_html = generate_tailwind
