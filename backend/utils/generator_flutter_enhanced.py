"""
Flutter/Dart Code Generator - STYLE-AWARE UPGRADE.

Generates complete main.dart with:
  - MaterialApp with theme from ILS colors
  - TextEditingController for form inputs
  - ElevatedButton with SnackBar feedback
  - Proper spacing using SizedBox
  - Card-based layouts with BoxDecoration
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def hex_to_dart_color(hex_color: str) -> str:
    """Convert hex color to Dart Color format."""
    hex_color = hex_color.lstrip('#')
    return f"Color(0xFF{hex_color.upper()})"


def generate_flutter_code(ils: Dict[str, Any]) -> str:
    """
    Generate complete Flutter main.dart from ILS.
    
    Args:
        ils: Intermediate Layout Schema with style
        
    Returns:
        Dart code as string
    """
    logger.info("Generating Flutter code from ILS")
    
    title = ils.get('title', 'Generated UI')
    page_style = ils.get('style', {})
    sections = ils.get('sections', [])
    
    # Extract colors
    bg_color = page_style.get('background_color', '#f5f6fa')
    primary_color = page_style.get('primary_color', '#2563eb')
    accent_color = page_style.get('accent_color', '#f59e0b')
    
    # Convert to Dart colors
    dart_primary = hex_to_dart_color(primary_color)
    dart_bg = hex_to_dart_color(bg_color)
    dart_accent = hex_to_dart_color(accent_color)
    
    # Generate parts
    imports = generate_imports()
    controllers = generate_controllers(sections)
    dispose_method = generate_dispose(sections)
    widgets = generate_widgets(sections, page_style)
    
    code = f'''{imports}

void main() => runApp(const GeneratedApp());

class GeneratedApp extends StatelessWidget {{
  const GeneratedApp({{Key? key}}) : super(key: key);

  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      title: '{title}',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: {dart_primary},
        colorScheme: ColorScheme.fromSeed(
          seedColor: {dart_primary},
          background: {dart_bg},
        ),
        scaffoldBackgroundColor: {dart_bg},
        useMaterial3: true,
      ),
      home: const GeneratedPage(),
    );
  }}
}}

class GeneratedPage extends StatefulWidget {{
  const GeneratedPage({{Key? key}}) : super(key: key);

  @override
  State<GeneratedPage> createState() => _GeneratedPageState();
}}

class _GeneratedPageState extends State<GeneratedPage> {{
{controllers}

{dispose_method}

  void _handleSubmit() {{
    // Get form data
    final data = {{}};
    // Show success message
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Form submitted successfully!'),
        backgroundColor: Colors.green,
      ),
    );
  }}

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{title}'),
        elevation: 0,
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
{widgets}
            ],
          ),
        ),
      ),
    );
  }}
}}
'''
    
    logger.info("Generated Flutter code")
    return code


def generate_imports() -> str:
    """Generate Flutter imports."""
    return "import 'package:flutter/material.dart';"


def generate_controllers(sections: List[Dict[str, Any]]) -> str:
    """Generate TextEditingController declarations."""
    form_sections = [s for s in sections if s.get('type') == 'form']
    
    if not form_sections:
        return ""
    
    controllers = []
    for section in form_sections:
        fields = section.get('fields', section.get('elements', []))
        
        for field in fields:
            field_type = field.get('type', '')
            if field_type in ['text_input', 'email_input', 'password_input', 'textarea']:
                name = field.get('name', 'field')
                controllers.append(f"  final {name}Controller = TextEditingController();")
    
    return '\n'.join(controllers) if controllers else ""


def generate_dispose(sections: List[Dict[str, Any]]) -> str:
    """Generate dispose method for controllers."""
    form_sections = [s for s in sections if s.get('type') == 'form']
    
    if not form_sections:
        return ""
    
    disposes = ["  @override\n  void dispose() {"]
    
    for section in form_sections:
        fields = section.get('fields', section.get('elements', []))
        
        for field in fields:
            field_type = field.get('type', '')
            if field_type in ['text_input', 'email_input', 'password_input', 'textarea']:
                name = field.get('name', 'field')
                disposes.append(f"    {name}Controller.dispose();")
    
    disposes.append("    super.dispose();")
    disposes.append("  }")
    
    return '\n'.join(disposes) if len(disposes) > 2 else ""


def generate_widgets(sections: List[Dict[str, Any]], page_style: Dict[str, Any]) -> str:
    """Generate widgets for all sections."""
    widget_parts = []
    
    for i, section in enumerate(sections):
        section_type = section.get('type', 'content')
        
        if section_type == 'form':
            widget_parts.append(generate_form_widget(section, page_style))
        elif section_type == 'cards':
            widget_parts.append(generate_cards_widget(section, page_style))
        else:
            widget_parts.append(generate_content_widget(section, page_style))
        
        # Add spacing between sections
        if i < len(sections) - 1:
            widget_parts.append("              const SizedBox(height: 24.0),")
    
    return '\n'.join(widget_parts)


def generate_form_widget(section: Dict[str, Any], page_style: Dict[str, Any]) -> str:
    """Generate form widget."""
    fields = section.get('fields', section.get('elements', []))
    primary_action = section.get('primary_action')
    section_style = section.get('style', {})
    
    padding = section_style.get('padding', 24)
    gap = section_style.get('gap', 16)
    border_radius = section_style.get('border_radius', 16)
    
    primary_color = page_style.get('primary_color', '#2563eb')
    dart_primary = hex_to_dart_color(primary_color)
    
    widget_parts = [
        "              Container(",
        "                constraints: const BoxConstraints(maxWidth: 400),",
        "                decoration: BoxDecoration(",
        "                  color: Colors.white,",
        f"                  borderRadius: BorderRadius.circular({border_radius}.0),",
        "                  boxShadow: [",
        "                    BoxShadow(",
        "                      color: Colors.black.withOpacity(0.1),",
        "                      blurRadius: 10,",
        "                      offset: const Offset(0, 4),",
        "                    ),",
        "                  ],",
        "                ),",
        f"                padding: const EdgeInsets.all({padding}.0),",
        "                child: Column(",
        "                  crossAxisAlignment: CrossAxisAlignment.stretch,",
        "                  children: ["
    ]
    
    # Fields
    for i, field in enumerate(fields):
        field_widget = generate_field_widget(field, gap)
        if field_widget:
            widget_parts.append(field_widget)
            if i < len(fields) - 1:
                widget_parts.append(f"                    const SizedBox(height: {gap}.0),")
    
    # Button
    if primary_action:
        label = primary_action.get('label', 'Submit')
        widget_parts.extend([
            f"                    const SizedBox(height: {gap * 1.5}.0),",
            "                    ElevatedButton(",
            "                      onPressed: _handleSubmit,",
            "                      style: ElevatedButton.styleFrom(",
            f"                        backgroundColor: {dart_primary},",
            "                        foregroundColor: Colors.white,",
            "                        padding: const EdgeInsets.symmetric(vertical: 16.0),",
            f"                        shape: RoundedRectangleBorder(",
            f"                          borderRadius: BorderRadius.circular({min(border_radius, 12)}.0),",
            "                        ),",
            "                      ),",
            f"                      child: const Text(",
            f"                        '{label}',",
            "                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),",
            "                      ),",
            "                    ),"
        ])
    
    widget_parts.extend([
        "                  ],",
        "                ),",
        "              ),"
    ])
    
    return '\n'.join(widget_parts)


def generate_field_widget(field: Dict[str, Any], gap: int) -> str:
    """Generate widget for a form field."""
    field_type = field.get('type', 'text_input')
    label = field.get('label', '')
    name = field.get('name', 'field')
    placeholder = field.get('placeholder', '')
    
    if field_type in ['text_input', 'email_input', 'password_input']:
        obscure = 'true' if field_type == 'password_input' else 'false'
        keyboard_type = 'TextInputType.emailAddress' if field_type == 'email_input' else 'TextInputType.text'
        
        return f'''                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '{label}',
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                            color: Color(0xFF374151),
                          ),
                        ),
                        const SizedBox(height: 8.0),
                        TextField(
                          controller: {name}Controller,
                          obscureText: {obscure},
                          keyboardType: {keyboard_type},
                          decoration: InputDecoration(
                            hintText: '{placeholder}',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8.0),
                              borderSide: const BorderSide(color: Color(0xFFD1D5DB)),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8.0),
                              borderSide: const BorderSide(color: Color(0xFFD1D5DB)),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8.0),
                              borderSide: const BorderSide(color: Color(0xFF2563EB), width: 2),
                            ),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                          ),
                        ),
                      ],
                    ),'''
    
    elif field_type == 'textarea':
        return f'''                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '{label}',
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                            color: Color(0xFF374151),
                          ),
                        ),
                        const SizedBox(height: 8.0),
                        TextField(
                          controller: {name}Controller,
                          maxLines: 3,
                          decoration: InputDecoration(
                            hintText: '{placeholder}',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8.0),
                            ),
                            contentPadding: const EdgeInsets.all(12),
                          ),
                        ),
                      ],
                    ),'''
    
    elif field_type == 'text_block':
        return f'''                    Text(
                      '{label}',
                      style: const TextStyle(fontSize: 14, color: Color(0xFF6B7280)),
                    ),'''
    
    return ''


def generate_cards_widget(section: Dict[str, Any], page_style: Dict[str, Any]) -> str:
    """Generate cards widget."""
    cards = section.get('cards', [])
    section_style = section.get('style', {})
    gap = section_style.get('gap', 16)
    border_radius = section_style.get('border_radius', 12)
    
    widget_parts = [
        "              Wrap(",
        "                spacing: 16.0,",
        "                runSpacing: 16.0,",
        "                children: ["
    ]
    
    for card in cards:
        title = card.get('title', 'Card')
        body = card.get('body', 'Card content.')
        
        widget_parts.append(f'''                  Container(
                    width: 280,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular({border_radius}.0),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 6,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '{title}',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF111827),
                          ),
                        ),
                        const SizedBox(height: 12.0),
                        Text(
                          '{body}',
                          style: const TextStyle(
                            fontSize: 14,
                            color: Color(0xFF6B7280),
                          ),
                        ),
                      ],
                    ),
                  ),''')
    
    widget_parts.extend([
        "                ],",
        "              ),"
    ])
    
    return '\n'.join(widget_parts)


def generate_content_widget(section: Dict[str, Any], page_style: Dict[str, Any]) -> str:
    """Generate content widget."""
    elements = section.get('elements', [])
    
    widget_parts = [
        "              Column(",
        "                crossAxisAlignment: CrossAxisAlignment.start,",
        "                children: ["
    ]
    
    for element in elements:
        element_type = element.get('type', '')
        label = element.get('label', '')
        
        if element_type == 'text_block':
            widget_parts.append(f'''                  Text(
                    '{label}',
                    style: const TextStyle(fontSize: 16, color: Color(0xFF4B5563)),
                  ),''')
            widget_parts.append("                  const SizedBox(height: 12.0),")
    
    widget_parts.extend([
        "                ],",
        "              ),"
    ])
    
    return '\n'.join(widget_parts)
