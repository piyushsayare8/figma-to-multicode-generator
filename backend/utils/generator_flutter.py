"""
Flutter/Dart Code Generator.

This module generates production-ready Flutter widgets
from an Intermediate Layout Schema (ILS).
"""

import logging
from typing import Dict, Any, List
import json

from config import Config

logger = logging.getLogger(__name__)

class FlutterGenerator:
    """Generator for Flutter/Dart code."""
    
    def __init__(self):
        self.config = Config()
        self.controller_counter = 0
        self.imports = set()
        
    def _generate_unique_controller_name(self, field_name: str) -> str:
        """Generate a unique controller name."""
        clean_name = field_name.replace(' ', '').replace('-', '').replace('_', '').lower()
        return f"_{clean_name}Controller"
    
    def _add_import(self, import_statement: str):
        """Add an import statement to the imports set."""
        self.imports.add(import_statement)
    
    def generate_form_section(self, section: Dict[str, Any]) -> str:
        """Generate Dart code for a form section."""
        elements = section.get('elements', [])
        primary_action = section.get('primary_action', {})
        secondary_actions = section.get('secondary_actions', [])
        title = section.get('title', 'Form')
        
        # Add required imports
        self._add_import("import 'package:flutter/material.dart';")
        
        widgets = []
        controllers = []
        
        # Form header
        widgets.append(f'Text(\n'
                      f'  "{title}",\n'
                      f'  style: const TextStyle(\n'
                      f'    fontSize: 24,\n'
                      f'    fontWeight: FontWeight.bold,\n'
                      f'  ),\n'
                      f'),')
        widgets.append('const SizedBox(height: 24),')
        
        # Form elements
        for element in elements:
            element_widgets, element_controllers = self.generate_form_element(element)
            widgets.extend(element_widgets)
            controllers.extend(element_controllers)
        
        # Actions
        if primary_action or secondary_actions:
            widgets.append('const SizedBox(height: 24),')
            
            if len(secondary_actions) > 0 or primary_action:
                widgets.append('Row(')
                widgets.append('  mainAxisAlignment: MainAxisAlignment.spaceEvenly,')
                widgets.append('  children: [')
                
                # Secondary actions first
                for i, action in enumerate(secondary_actions):
                    if i > 0:
                        widgets.append('    const SizedBox(width: 12),')
                    widgets.extend(self.generate_button_element(action, secondary=True))
                
                # Primary action
                if primary_action:
                    if len(secondary_actions) > 0:
                        widgets.append('    const SizedBox(width: 12),')
                    widgets.extend(self.generate_button_element(primary_action, secondary=False))
                
                widgets.append('  ],')
                widgets.append('),')
        
        return widgets, controllers
    
    def generate_form_element(self, element: Dict[str, Any]) -> tuple:
        """Generate Dart code for a single form element."""
        element_type = element.get('type', '')
        label = element.get('label', '')
        name = element.get('name', element.get('label', 'field'))
        placeholder = element.get('placeholder', '')
        required = element.get('required', False)
        
        widgets = []
        controllers = []
        
        if element_type in ['text_input', 'email_input', 'password_input']:
            controller_name = self._generate_unique_controller_name(name)
            controllers.append(controller_name)
            
            is_password = element_type == 'password_input'
            keyboard_type = 'TextInputType.emailAddress' if element_type == 'email_input' else 'TextInputType.text'
            
            widgets.extend([
                f'TextFormField(',
                f'  controller: {controller_name},',
                f'  obscureText: {str(is_password).lower()},',
                f'  keyboardType: {keyboard_type},',
                f'  decoration: const InputDecoration(',
                f'    labelText: "{label}",',
                f'    hintText: "{placeholder}",',
                f'    border: OutlineInputBorder(),',
                f'  ),',
                f'  validator: (value) {{',
                f'    if (value == null || value.isEmpty) {{',
                f'      return "Please enter {label.lower()}";',
                f'    }}',
                f'    return null;',
                f'  }},',
                f'),',
                'const SizedBox(height: 16),'
            ])
        
        elif element_type == 'textarea':
            controller_name = self._generate_unique_controller_name(name)
            controllers.append(controller_name)
            
            widgets.extend([
                f'TextFormField(',
                f'  controller: {controller_name},',
                f'  maxLines: 4,',
                f'  decoration: const InputDecoration(',
                f'    labelText: "{label}",',
                f'    hintText: "{placeholder}",',
                f'    border: OutlineInputBorder(),',
                f'    alignLabelWithHint: true,',
                f'  ),',
                f'  validator: (value) {{',
                f'    if (value == null || value.isEmpty) {{',
                f'      return "Please enter {label.lower()}";',
                f'    }}',
                f'    return null;',
                f'  }},',
                f'),',
                'const SizedBox(height: 16),'
            ])
        
        elif element_type == 'text_block':
            widgets.extend([
                f'Text(',
                f'  "{label}",',
                f'  style: const TextStyle(',
                f'    color: Colors.grey,',
                f'    fontSize: 14,',
                f'  ),',
                f'),',
                'const SizedBox(height: 8),'
            ])
        
        return widgets, controllers
    
    def generate_button_element(self, button: Dict[str, Any], secondary: bool = False) -> List[str]:
        """Generate Dart code for a button element."""
        label = button.get('label', 'Button')
        
        if secondary:
            return [
                'Expanded(',
                '  child: OutlinedButton(',
                '    onPressed: _onCancel,',
                '    style: OutlinedButton.styleFrom(',
                '      padding: const EdgeInsets.symmetric(vertical: 16),',
                '    ),',
                f'    child: Text("{label}"),',
                '  ),',
                '),'
            ]
        else:
            return [
                'Expanded(',
                '  child: ElevatedButton(',
                '    onPressed: _onSubmit,',
                '    style: ElevatedButton.styleFrom(',
                '      padding: const EdgeInsets.symmetric(vertical: 16),',
                '    ),',
                f'    child: Text("{label}"),',
                '  ),',
                '),'
            ]
    
    def generate_cards_section(self, section: Dict[str, Any]) -> List[str]:
        """Generate Dart code for a cards section."""
        elements = section.get('elements', [])
        title = section.get('title', 'Cards')
        
        widgets = []
        
        # Section header
        widgets.extend([
            f'Text(',
            f'  "{title}",',
            f'  style: const TextStyle(',
            f'    fontSize: 28,',
            f'    fontWeight: FontWeight.bold,',
            f'  ),',
            f'  textAlign: TextAlign.center,',
            f'),',
            'const SizedBox(height: 24),'
        ])
        
        # Cards grid
        if elements:
            card_widgets = []
            for element in elements:
                if element.get('type') == 'card':
                    card_widgets.extend(self.generate_card_element(element))
            
            if card_widgets:
                widgets.extend([
                    'GridView.builder(',
                    '  shrinkWrap: true,',
                    '  physics: const NeverScrollableScrollPhysics(),',
                    '  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(',
                    '    crossAxisCount: 2,',
                    '    crossAxisSpacing: 16,',
                    '    mainAxisSpacing: 16,',
                    '    childAspectRatio: 0.8,',
                    '  ),',
                    f'  itemCount: {len([e for e in elements if e.get("type") == "card"])},',
                    '  itemBuilder: (context, index) {',
                    '    final cards = [',
                    *['      ' + line for line in card_widgets],
                    '    ];',
                    '    return cards[index];',
                    '  },',
                    '),'
                ])
        
        return widgets
    
    def generate_card_element(self, element: Dict[str, Any]) -> List[str]:
        """Generate Dart code for a single card element."""
        label = element.get('label', 'Card')
        value = element.get('value', 'Card content goes here.')
        
        return [
            'Card(',
            '  elevation: 4,',
            '  shape: RoundedRectangleBorder(',
            '    borderRadius: BorderRadius.circular(12),',
            '  ),',
            '  child: Padding(',
            '    padding: const EdgeInsets.all(16),',
            '    child: Column(',
            '      crossAxisAlignment: CrossAxisAlignment.start,',
            '      children: [',
            f'        Text(',
            f'          "{label}",',
            f'          style: const TextStyle(',
            f'            fontSize: 18,',
            f'            fontWeight: FontWeight.w600,',
            f'          ),',
            f'        ),',
            '        const SizedBox(height: 8),',
            f'        Text(',
            f'          "{value}",',
            f'          style: const TextStyle(',
            f'            color: Colors.grey,',
            f'          ),',
            f'        ),',
            '      ],',
            '    ),',
            '  ),',
            '),'
        ]
    
    def generate_content_section(self, section: Dict[str, Any]) -> List[str]:
        """Generate Dart code for a content section."""
        elements = section.get('elements', [])
        title = section.get('title', 'Content')
        
        widgets = []
        
        # Section header
        widgets.extend([
            f'Text(',
            f'  "{title}",',
            f'  style: const TextStyle(',
            f'    fontSize: 28,',
            f'    fontWeight: FontWeight.bold,',
            f'  ),',
            f'),',
            'const SizedBox(height: 24),'
        ])
        
        # Content elements
        for element in elements:
            widgets.extend(self.generate_content_element(element))
        
        return widgets
    
    def generate_content_element(self, element: Dict[str, Any]) -> List[str]:
        """Generate Dart code for a single content element."""
        element_type = element.get('type', '')
        label = element.get('label', '')
        value = element.get('value', '')
        
        if element_type == 'text_block':
            return [
                f'Text(',
                f'  "{label}",',
                f'  style: const TextStyle(',
                f'    fontSize: 16,',
                f'    height: 1.7,',
                f'  ),',
                f'),',
                'const SizedBox(height: 16),'
            ]
        
        elif element_type == 'image_block':
            return [
                'Center(',
                '  child: ClipRRect(',
                '    borderRadius: BorderRadius.circular(8),',
                f'    child: Image.network(',
                f'      "{value}",',
                f'      errorBuilder: (context, error, stackTrace) => Container(',
                f'        height: 200,',
                f'        color: Colors.grey[300],',
                f'        child: const Center(',
                f'          child: Icon(Icons.image, size: 48),',
                f'        ),',
                f'      ),',
                f'    ),',
                '  ),',
                '),',
                'const SizedBox(height: 16),'
            ]
        
        return []
    
    def generate_widget_structure(self, ils: Dict[str, Any]) -> str:
        """Generate the complete Flutter widget structure."""
        title = ils.get('title', 'Generated UI')
        sections = ils.get('sections', [])
        
        # Generate sections code
        all_widgets = []
        all_controllers = []
        has_form = any(section.get('type') == 'form' for section in sections)
        
        for section in sections:
            section_type = section.get('type', '')
            
            if section_type == 'form':
                section_widgets, section_controllers = self.generate_form_section(section)
                all_widgets.extend(section_widgets)
                all_controllers.extend(section_controllers)
            elif section_type == 'cards':
                section_widgets = self.generate_cards_section(section)
                all_widgets.extend(section_widgets)
            elif section_type == 'content':
                section_widgets = self.generate_content_section(section)
                all_widgets.extend(section_widgets)
            else:
                # Default content section
                section_widgets = self.generate_content_section(section)
                all_widgets.extend(section_widgets)
        
        # Generate class name
        class_name = title.replace(' ', '').replace('-', '').replace('_', '')
        import re
        class_name = re.sub(r'[^a-zA-Z0-9]', '', class_name) or 'GeneratedWidget'
        if not class_name[0].isupper():
            class_name = class_name[0].upper() + class_name[1:]
        class_name += 'Page'
        
        # Generate controller declarations
        controllers_code = ""
        dispose_code = ""
        if all_controllers:
            controllers_code = "\n  // Form controllers\n"
            for controller in set(all_controllers):
                controllers_code += f"  final {controller} = TextEditingController();\n"
            
            dispose_code = """
  @override
  void dispose() {""" + "\n"
            for controller in set(all_controllers):
                dispose_code += f"    {controller}.dispose();\n"
            dispose_code += """    super.dispose();
  }"""
        
        # Generate form key if needed
        form_key_code = ""
        form_wrapper_start = ""
        form_wrapper_end = ""
        
        if has_form:
            form_key_code = "  final _formKey = GlobalKey<FormState>();\n"
            form_wrapper_start = "        Form(\n          key: _formKey,\n          child: Column(\n            children: ["
            form_wrapper_end = "            ],\n          ),\n        ),"
        
        # Generate event handlers
        handlers_code = ""
        if has_form:
            handlers_code = """
  void _onSubmit() {
    if (_formKey.currentState!.validate()) {
      // Process form data
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Form submitted successfully!')),
      );
    }
  }

  void _onCancel() {
    // Clear form data""" + "\n"
            for controller in set(all_controllers):
                handlers_code += f"    {controller}.clear();\n"
            handlers_code += """  }"""
        
        # Generate imports
        imports_list = list(self.imports) if self.imports else ["import 'package:flutter/material.dart';"]
        
        # Generate widgets content
        widgets_content = "\n          ".join(all_widgets) if all_widgets else 'const Text("No content available"),'
        
        # Wrap in form if needed
        if has_form:
            widgets_content = form_wrapper_start + "\n            " + widgets_content.replace('\n          ', '\n            ') + "\n" + form_wrapper_end
        
        # Complete widget template
        widget_template = f'''{' '.join(imports_list)}

class {class_name} extends StatefulWidget {{
  const {class_name}({{Key? key}}) : super(key: key);

  @override
  State<{class_name}> createState() => _{class_name}State();
}}

class _{class_name}State extends State<{class_name}> {{
{form_key_code}{controllers_code}{dispose_code}{handlers_code}

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{title}'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: Container(
        padding: const EdgeInsets.all(16),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              {widgets_content}
            ],
          ),
        ),
      ),
    );
  }}
}}'''
        
        return widget_template

def generate_flutter(ils: Dict[str, Any]) -> str:
    """
    Generate Flutter/Dart widget from an ILS.
    
    This is the main function called by the API endpoint.
    
    Args:
        ils: Intermediate Layout Schema dictionary
        
    Returns:
        Complete Flutter widget code
    """
    logger.debug(f"Generating Flutter code from ILS: {ils.get('title', 'Unknown')}")
    
    if not ils or not isinstance(ils, dict):
        logger.error("Invalid ILS provided for Flutter generation")
        return '''import 'package:flutter/material.dart';

class ErrorWidget extends StatelessWidget {
  const ErrorWidget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Text('Invalid UI specification'),
      ),
    );
  }
}'''
    
    generator = FlutterGenerator()
    
    try:
        flutter_code = generator.generate_widget_structure(ils)
        logger.info(f"Successfully generated Flutter code ({len(flutter_code)} characters)")
        return flutter_code
        
    except Exception as e:
        logger.error(f"Error generating Flutter code: {str(e)}")
        # Return error widget
        return f'''import 'package:flutter/material.dart';

class ErrorWidget extends StatelessWidget {{
  const ErrorWidget({{Key? key}}) : super(key: key);

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(title: const Text('Generation Error')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              'Generation Error',
              style: TextStyle(fontSize: 24, color: Colors.red),
            ),
            const SizedBox(height: 16),
            Text('Failed to generate code: {str(e)}'),
          ],
        ),
      ),
    );
  }}
}}'''

# Backward compatibility aliases
generate_flutter_code = generate_flutter
