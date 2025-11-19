"""
React Component Generator - STYLE-AWARE UPGRADE.

Generates a complete React component with:
  - Proper imports (React)
  - className attributes (not class)
  - Tailwind CSS or inline styles
  - useState hooks for form handling
  - handleSubmit with preventDefault
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def generate_react_component(ils: Dict[str, Any]) -> str:
    """
    Generate React component from ILS with improved formatting and functionality.
    
    Args:
        ils: Intermediate Layout Schema with style
        
    Returns:
        React component code as string
    """
    logger.info("Generating React component from ILS")
    
    title = ils.get('title', 'Generated UI')
    page_style = ils.get('style', {})
    sections = ils.get('sections', [])
    
    # Extract colors with fallbacks
    bg_color = page_style.get('background_color', '#f5f6fa')
    primary_color = page_style.get('primary_color', '#2563eb')
    text_color = page_style.get('text_color', '#111827')
    
    # Generate component parts
    imports = generate_imports(sections)
    state_hooks = generate_state_hooks(sections)
    handlers = generate_handlers(sections)
    jsx = generate_jsx(sections, page_style)
    
    # Improved component structure with better formatting
    component = f'''{imports}

export const GeneratedPage = () => {{
  // State management
{state_hooks}

  // Event handlers
{handlers}

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4 sm:p-8"
      style={{{{ 
        backgroundColor: '{bg_color}',
        color: '{text_color}'
      }}}}
    >
      <div className="w-full max-w-7xl">
{jsx}
      </div>
    </div>
  );
}};

export default GeneratedPage;
'''
    
    logger.info("Generated React component with enhanced features")
    return component


def generate_imports(sections: List[Dict[str, Any]]) -> str:
    """Generate import statements."""
    has_form = any(s.get('type') == 'form' for s in sections)
    
    if has_form:
        return "import React, { useState } from 'react';"
    else:
        return "import React from 'react';"


def generate_state_hooks(sections: List[Dict[str, Any]]) -> str:
    """Generate useState hooks for forms."""
    form_sections = [s for s in sections if s.get('type') == 'form']
    
    if not form_sections:
        return ""
    
    hooks = []
    for i, section in enumerate(form_sections):
        fields = section.get('fields', section.get('elements', []))
        
        for field in fields:
            field_type = field.get('type', '')
            if field_type in ['text_input', 'email_input', 'password_input', 'textarea']:
                name = field.get('name', 'field')
                hooks.append(f"  const [{name}, set{name.capitalize()}] = useState('');")
    
    return '\n'.join(hooks) if hooks else ""


def generate_handlers(sections: List[Dict[str, Any]]) -> str:
    """Generate event handlers."""
    has_form = any(s.get('type') == 'form' for s in sections)
    
    if not has_form:
        return ""
    
    return '''
  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    console.log('Form submitted:', data);
    alert('Form submitted successfully! Check console for data.');
  };'''


def generate_jsx(sections: List[Dict[str, Any]], page_style: Dict[str, Any]) -> str:
    """Generate JSX for all sections."""
    jsx_parts = []
    
    for section in sections:
        section_type = section.get('type', 'content')
        
        if section_type == 'form':
            jsx_parts.append(generate_form_jsx(section, page_style))
        elif section_type == 'cards':
            jsx_parts.append(generate_cards_jsx(section, page_style))
        else:
            jsx_parts.append(generate_content_jsx(section, page_style))
    
    return '\n'.join(jsx_parts)


def generate_form_jsx(section: Dict[str, Any], page_style: Dict[str, Any]) -> str:
    """Generate JSX for form section."""
    fields = section.get('fields', section.get('elements', []))
    primary_action = section.get('primary_action')
    secondary_actions = section.get('secondary_actions', [])
    section_style = section.get('style', {})
    
    primary_color = page_style.get('primary_color', '#2563eb')
    
    jsx_parts = [
        '        <div className="max-w-md mx-auto">',
        '          <div className="bg-white rounded-xl shadow-lg p-6">',
        '            <form className="space-y-4" onSubmit={handleSubmit}>'
    ]
    
    # Fields
    for field in fields:
        field_jsx = generate_field_jsx(field)
        if field_jsx:
            jsx_parts.append(field_jsx)
    
    # Actions
    if primary_action or secondary_actions:
        jsx_parts.append('              <div className="flex space-x-3 pt-4">')
        
        for action in secondary_actions:
            label = action.get('label', 'Cancel')
            jsx_parts.append(f'''                <button
                  type="button"
                  className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {label}
                </button>''')
        
        if primary_action:
            label = primary_action.get('label', 'Submit')
            jsx_parts.append(f'''                <button
                  type="submit"
                  className="flex-1 px-4 py-2 text-sm font-medium text-white rounded-lg transition-all hover:opacity-90"
                  style={{{{ backgroundColor: '{primary_color}' }}}}
                >
                  {label}
                </button>''')
        
        jsx_parts.append('              </div>')
    
    jsx_parts.extend([
        '            </form>',
        '          </div>',
        '        </div>'
    ])
    
    return '\n'.join(jsx_parts)


def generate_field_jsx(field: Dict[str, Any]) -> str:
    """Generate JSX for a form field."""
    field_type = field.get('type', 'text_input')
    label = field.get('label', '')
    name = field.get('name', 'field')
    placeholder = field.get('placeholder', '')
    required = field.get('required', False)
    
    if field_type in ['text_input', 'email_input']:
        input_type = 'email' if field_type == 'email_input' else 'text'
        return f'''              <div>
                <label htmlFor="{name}" className="block text-sm font-medium text-gray-700 mb-1">
                  {label}
                </label>
                <input
                  type="{input_type}"
                  id="{name}"
                  name="{name}"
                  placeholder="{placeholder}"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  {' required' if required else ''}
                />
              </div>'''
    
    elif field_type == 'password_input':
        return f'''              <div>
                <label htmlFor="{name}" className="block text-sm font-medium text-gray-700 mb-1">
                  {label}
                </label>
                <input
                  type="password"
                  id="{name}"
                  name="{name}"
                  placeholder="{placeholder}"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  {' required' if required else ''}
                />
              </div>'''
    
    elif field_type == 'textarea':
        return f'''              <div>
                <label htmlFor="{name}" className="block text-sm font-medium text-gray-700 mb-1">
                  {label}
                </label>
                <textarea
                  id="{name}"
                  name="{name}"
                  placeholder="{placeholder}"
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  {' required' if required else ''}
                />
              </div>'''
    
    elif field_type == 'text_block':
        return f'              <p className="text-sm text-gray-600">{label}</p>'
    
    return ''


def generate_cards_jsx(section: Dict[str, Any], page_style: Dict[str, Any]) -> str:
    """Generate JSX for cards section."""
    cards = section.get('cards', [])
    section_style = section.get('style', {})
    columns = section_style.get('columns', 3)
    
    grid_cols = 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' if columns == 3 else f'grid-cols-1 md:grid-cols-{min(columns, 4)}'
    
    jsx_parts = [
        '        <div className="max-w-6xl mx-auto px-4 py-8">',
        f'          <div className="grid {grid_cols} gap-6">'
    ]
    
    for card in cards:
        title = card.get('title', 'Card')
        body = card.get('body', 'Card content.')
        
        jsx_parts.append(f'''            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">{title}</h3>
              <p className="text-gray-600">{body}</p>
            </div>''')
    
    jsx_parts.extend([
        '          </div>',
        '        </div>'
    ])
    
    return '\n'.join(jsx_parts)


def generate_content_jsx(section: Dict[str, Any], page_style: Dict[str, Any]) -> str:
    """Generate JSX for content section."""
    elements = section.get('elements', [])
    
    jsx_parts = [
        '        <div className="max-w-4xl mx-auto px-4 py-8">',
        '          <div className="space-y-6">'
    ]
    
    for element in elements:
        element_type = element.get('type', '')
        label = element.get('label', '')
        value = element.get('value', '')
        
        if element_type == 'text_block':
            jsx_parts.append(f'            <p className="text-gray-700">{label}</p>')
        elif element_type == 'image_block':
            jsx_parts.append(f'            <img src="{value}" alt="{label}" className="w-full h-auto rounded-lg shadow-md" />')
    
    jsx_parts.extend([
        '          </div>',
        '        </div>'
    ])
    
    return '\n'.join(jsx_parts)
