"""
React JSX Code Generator.

This module generates production-ready React JSX components
from an Intermediate Layout Schema (ILS).
"""

import logging
from typing import Dict, Any, List
import json

from config import Config

logger = logging.getLogger(__name__)

class ReactGenerator:
    """Generator for React JSX code."""
    
    def __init__(self):
        self.config = Config()
        self.component_counter = 0
        self.imports = set()
        
    def _generate_unique_name(self, prefix: str = "Component") -> str:
        """Generate a unique component name."""
        self.component_counter += 1
        return f"{prefix}{self.component_counter}"
    
    def _add_import(self, import_statement: str):
        """Add an import statement to the imports set."""
        self.imports.add(import_statement)
    
    def generate_form_section(self, section: Dict[str, Any]) -> str:
        """Generate JSX for a form section."""
        elements = section.get('elements', [])
        primary_action = section.get('primary_action', {})
        secondary_actions = section.get('secondary_actions', [])
        title = section.get('title', 'Form')
        
        # Add required imports
        self._add_import("import React, { useState } from 'react';")
        
        jsx_parts = []
        
        # Form container start
        jsx_parts.append(f'''
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">{title}</h2>
      <form onSubmit={{handleSubmit}} className="space-y-4">''')
        
        # Form elements
        for element in elements:
            element_jsx = self.generate_form_element(element)
            if element_jsx:
                jsx_parts.append(element_jsx)
        
        # Actions
        if primary_action or secondary_actions:
            jsx_parts.append('        <div className="flex space-x-3 pt-4">')
            
            # Secondary actions first
            for action in secondary_actions:
                jsx_parts.append(self.generate_button_element(action, secondary=True))
            
            # Primary action
            if primary_action:
                jsx_parts.append(self.generate_button_element(primary_action, secondary=False))
            
            jsx_parts.append('        </div>')
        
        # Form container end
        jsx_parts.append('''      </form>
    </div>''')
        
        return '\n'.join(jsx_parts)
    
    def generate_form_element(self, element: Dict[str, Any]) -> str:
        """Generate JSX for a single form element."""
        element_type = element.get('type', '')
        label = element.get('label', '')
        name = element.get('name', '')
        placeholder = element.get('placeholder', '')
        required = element.get('required', False)
        
        if element_type in ['text_input', 'email_input', 'password_input']:
            input_type = 'text'
            if element_type == 'password_input':
                input_type = 'password'
            elif element_type == 'email_input':
                input_type = 'email'
                
            return f'''        <div>
          <label htmlFor="{name}" className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
          <input
            type="{input_type}"
            id="{name}"
            name="{name}"
            placeholder="{placeholder}"
            value={{formData.{name} || ''}}
            onChange={{handleInputChange}}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            {"required" if required else ""}
          />
        </div>'''
        
        elif element_type == 'textarea':
            return f'''        <div>
          <label htmlFor="{name}" className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
          <textarea
            id="{name}"
            name="{name}"
            placeholder="{placeholder}"
            value={{formData.{name} || ''}}
            onChange={{handleInputChange}}
            rows="3"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            {"required" if required else ""}
          />
        </div>'''
        
        elif element_type == 'text_block':
            return f'''        <div className="text-sm text-gray-600">
          {label}
        </div>'''
        
        return ''
    
    def generate_button_element(self, button: Dict[str, Any], secondary: bool = False) -> str:
        """Generate JSX for a button element."""
        label = button.get('label', 'Button')
        
        if secondary:
            return f'''          <button
            type="button"
            onClick={{handleCancel}}
            className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            {label}
          </button>'''
        else:
            return f'''          <button
            type="submit"
            className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            {label}
          </button>'''
    
    def generate_cards_section(self, section: Dict[str, Any]) -> str:
        """Generate JSX for a cards section."""
        elements = section.get('elements', [])
        title = section.get('title', 'Cards')
        
        jsx_parts = []
        
        # Cards container start
        jsx_parts.append(f'''
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">{title}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">''')
        
        # Cards
        for element in elements:
            if element.get('type') == 'card':
                card_jsx = self.generate_card_element(element)
                jsx_parts.append(card_jsx)
        
        # Cards container end
        jsx_parts.append('''      </div>
    </div>''')
        
        return '\n'.join(jsx_parts)
    
    def generate_card_element(self, element: Dict[str, Any]) -> str:
        """Generate JSX for a single card element."""
        label = element.get('label', 'Card')
        value = element.get('value', 'Card content goes here.')
        
        return f'''        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-3">{label}</h3>
          <p className="text-gray-600">{value}</p>
        </div>'''
    
    def generate_content_section(self, section: Dict[str, Any]) -> str:
        """Generate JSX for a content section."""
        elements = section.get('elements', [])
        title = section.get('title', 'Content')
        
        jsx_parts = []
        
        # Content container start
        jsx_parts.append(f'''
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">{title}</h2>
      <div className="space-y-6">''')
        
        # Content elements
        for element in elements:
            element_jsx = self.generate_content_element(element)
            if element_jsx:
                jsx_parts.append(element_jsx)
        
        # Content container end
        jsx_parts.append('''      </div>
    </div>''')
        
        return '\n'.join(jsx_parts)
    
    def generate_content_element(self, element: Dict[str, Any]) -> str:
        """Generate JSX for a single content element."""
        element_type = element.get('type', '')
        label = element.get('label', '')
        value = element.get('value', '')
        
        if element_type == 'text_block':
            return f'''        <div className="prose max-w-none">
          <p className="text-gray-700 leading-relaxed">{label}</p>
        </div>'''
        
        elif element_type == 'image_block':
            return f'''        <div className="flex justify-center">
          <img src="{value}" alt="{label}" className="max-w-full h-auto rounded-lg shadow-md" />
        </div>'''
        
        return ''
    
    def generate_component_structure(self, ils: Dict[str, Any]) -> str:
        """Generate the complete React component structure."""
        title = ils.get('title', 'Generated UI')
        sections = ils.get('sections', [])
        
        # Generate sections JSX
        sections_jsx = []
        has_form = any(section.get('type') == 'form' for section in sections)
        
        for section in sections:
            section_type = section.get('type', '')
            
            if section_type == 'form':
                section_jsx = self.generate_form_section(section)
            elif section_type == 'cards':
                section_jsx = self.generate_cards_section(section)
            elif section_type == 'content':
                section_jsx = self.generate_content_section(section)
            else:
                # Default content section
                section_jsx = self.generate_content_section(section)
            
            sections_jsx.append(section_jsx)
        
        # Generate state management code for forms
        state_code = ""
        handlers_code = ""
        
        if has_form:
            # Find all form fields to generate state
            form_fields = []
            for section in sections:
                if section.get('type') == 'form':
                    for element in section.get('elements', []):
                        if element.get('name'):
                            form_fields.append(element.get('name'))
            
            if form_fields:
                fields_init = {field: "" for field in form_fields}
                state_code = f'''
  const [formData, setFormData] = useState({json.dumps(fields_init, indent=4).replace('"', "'")});'''
                
                handlers_code = '''
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    // Add your form submission logic here
  };

  const handleCancel = () => {
    setFormData({});
    console.log('Form cancelled');
  };'''
        
        # Generate component name
        component_name = title.replace(' ', '').replace('-', '').replace('_', '')
        # Remove any non-alphanumeric characters
        import re
        component_name = re.sub(r'[^a-zA-Z0-9]', '', component_name) or 'GeneratedComponent'
        if not component_name[0].isupper():
            component_name = component_name[0].upper() + component_name[1:]
        
        # Generate imports
        imports_list = list(self.imports) if self.imports else ["import React from 'react';"]
        if has_form and "import React, { useState } from 'react';" not in imports_list:
            imports_list = ["import React, { useState } from 'react';"]
        
        # Complete component template
        component_template = f'''{' '.join(imports_list)}

const {component_name} = () => {{{state_code}{handlers_code}

  return (
    <div className="bg-gray-50 min-h-screen">
      <div className="py-12">
{''.join(sections_jsx)}
      </div>
    </div>
  );
}};

export default {component_name};'''
        
        return component_template

def generate_react(ils: Dict[str, Any]) -> str:
    """
    Generate React JSX component from an ILS.
    
    This is the main function called by the API endpoint.
    
    Args:
        ils: Intermediate Layout Schema dictionary
        
    Returns:
        Complete React component code
    """
    logger.debug(f"Generating React code from ILS: {ils.get('title', 'Unknown')}")
    
    if not ils or not isinstance(ils, dict):
        logger.error("Invalid ILS provided for React generation")
        return '''import React from 'react';

const ErrorComponent = () => {
  return <div>Invalid UI specification</div>;
};

export default ErrorComponent;'''
    
    generator = ReactGenerator()
    
    try:
        react_code = generator.generate_component_structure(ils)
        logger.info(f"Successfully generated React code ({len(react_code)} characters)")
        return react_code
        
    except Exception as e:
        logger.error(f"Error generating React code: {str(e)}")
        # Return error component
        return f'''import React from 'react';

const ErrorComponent = () => {{
  return (
    <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
      <h1>Generation Error</h1>
      <p>Failed to generate code: {str(e)}</p>
    </div>
  );
}};

export default ErrorComponent;'''

# Backward compatibility aliases
generate_react_component = generate_react
