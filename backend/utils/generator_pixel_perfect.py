"""
Pixel-Perfect Code Generators - Visual Design Replication.

Generates code that visually matches the original UI design using:
- Extracted colors (background, text, borders)
- Extracted text content (OCR)
- Exact positioning and sizing
- Border radius, shadows, padding
- Font sizes

Supports: HTML/CSS, Tailwind, React, Flutter
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# HTML + CSS (Pixel-Perfect)
# ============================================================================

def generate_pixel_perfect_html_css(
    ils: Dict[str, Any],
    blocks: List[Dict[str, Any]]
) -> Tuple[str, str]:
    """
    Generate pixel-perfect HTML and CSS.
    
    Uses absolute positioning to match exact layout from design.
    """
    logger.info("Generating pixel-perfect HTML + CSS")
    
    # Extract dimensions
    dims = ils.get('image_dimensions', {'width': 1024, 'height': 768})
    canvas_width = dims['width']
    canvas_height = dims['height']
    
    # Generate HTML
    html_elements = []
    css_rules = []
    
    for idx, block in enumerate(blocks):
        block_type = block.get('type', 'unknown')
        visual_style = block.get('visual_style', {})
        text = block.get('extracted_text', '')
        
        # Generate unique class
        class_name = f"element-{idx}"
        
        # Generate HTML element
        if block_type in ['text_input', 'input_field']:
            html_elements.append(f'  <input type="text" class="{class_name}" placeholder="{text or "Enter text"}">')
        elif block_type == 'password_input':
            html_elements.append(f'  <input type="password" class="{class_name}" placeholder="{text or "Password"}">')
        elif block_type == 'button':
            html_elements.append(f'  <button class="{class_name}">{text or "Button"}</button>')
        elif block_type in ['heading', 'text', 'text_block']:
            html_elements.append(f'  <div class="{class_name}">{text or "Text content"}</div>')
        elif block_type in ['image', 'image_block']:
            html_elements.append(f'  <div class="{class_name}"></div>')
        else:
            html_elements.append(f'  <div class="{class_name}">{text or ""}</div>')
        
        # Generate CSS for this element
        css_rule = generate_css_rule(class_name, block, visual_style)
        css_rules.append(css_rule)
    
    # Build complete HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated UI</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="canvas">
{chr(10).join(html_elements)}
</div>
</body>
</html>'''
    
    # Build complete CSS
    css = f'''/* Pixel-Perfect Generated Styles */

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    overflow-x: hidden;
}}

.canvas {{
    position: relative;
    width: {canvas_width}px;
    height: {canvas_height}px;
    margin: 0 auto;
    background: #f5f6fa;
}}

/* Element Styles */
{chr(10).join(css_rules)}

/* Input Resets */
input {{
    border: none;
    outline: none;
    font-family: inherit;
}}

button {{
    border: none;
    cursor: pointer;
    font-family: inherit;
}}
'''
    
    return html, css


def generate_css_rule(
    class_name: str,
    block: Dict[str, Any],
    visual_style: Dict[str, Any]
) -> str:
    """Generate CSS rule for a single element."""
    pos = visual_style.get('position', {})
    size = visual_style.get('size', {})
    colors = visual_style.get('colors', {})
    border = visual_style.get('border', {})
    shadow = visual_style.get('shadow', {})
    padding = visual_style.get('padding', {})
    
    x = pos.get('x', 0)
    y = pos.get('y', 0)
    width = size.get('width', 100)
    height = size.get('height', 40)
    
    bg_color = colors.get('background', '#ffffff')
    text_color = colors.get('text', '#000000')
    border_color = colors.get('border', '#cccccc')
    
    border_radius = visual_style.get('border_radius', 0)
    font_size = visual_style.get('font_size', 14)
    
    has_border = border.get('has_border', False)
    border_width = border.get('width', 1)
    
    has_shadow = shadow.get('has_shadow', False)
    shadow_str = f"{shadow.get('blur', 10)}px {shadow.get('spread', 2)}px {shadow.get('color', 'rgba(0,0,0,0.1)')}" if has_shadow else "none"
    
    pad_top = padding.get('top', 8)
    pad_right = padding.get('right', 12)
    pad_bottom = padding.get('bottom', 8)
    pad_left = padding.get('left', 12)
    
    css = f'''.{class_name} {{
    position: absolute;
    left: {x}px;
    top: {y}px;
    width: {width}px;
    height: {height}px;
    background-color: {bg_color};
    color: {text_color};
    font-size: {font_size}px;
    border-radius: {border_radius}px;
    padding: {pad_top}px {pad_right}px {pad_bottom}px {pad_left}px;
    display: flex;
    align-items: center;
    justify-content: center;
    {f'border: {border_width}px solid {border_color};' if has_border else ''}
    box-shadow: {shadow_str};
}}'''
    
    return css


# ============================================================================
# Tailwind (Pixel-Perfect)
# ============================================================================

def generate_pixel_perfect_tailwind(
    ils: Dict[str, Any],
    blocks: List[Dict[str, Any]]
) -> str:
    """Generate pixel-perfect HTML with Tailwind CSS."""
    logger.info("Generating pixel-perfect Tailwind HTML")
    
    dims = ils.get('image_dimensions', {'width': 1024, 'height': 768})
    
    elements = []
    
    for idx, block in enumerate(blocks):
        block_type = block.get('type', 'unknown')
        visual_style = block.get('visual_style', {})
        text = block.get('extracted_text', '')
        
        pos = visual_style.get('position', {})
        size = visual_style.get('size', {})
        colors = visual_style.get('colors', {})
        border_radius = visual_style.get('border_radius', 0)
        
        # Build Tailwind classes
        classes = ['absolute', 'flex', 'items-center', 'justify-center']
        
        # Add border radius class
        if border_radius > 0:
            if border_radius < 6:
                classes.append('rounded')
            elif border_radius < 12:
                classes.append('rounded-lg')
            else:
                classes.append('rounded-xl')
        
        # Build inline styles for exact positioning and colors
        style_parts = [
            f"left: {pos.get('x', 0)}px",
            f"top: {pos.get('y', 0)}px",
            f"width: {size.get('width', 100)}px",
            f"height: {size.get('height', 40)}px",
            f"backgroundColor: '{colors.get('background', '#fff')}'",
            f"color: '{colors.get('text', '#000')}'"
        ]
        style_str = '; '.join(style_parts)
        
        # Generate element
        if block_type in ['text_input', 'input_field']:
            elements.append(f'  <input type="text" class="{" ".join(classes)}" style="{style_str}" placeholder="{text or "Enter text"}">')
        elif block_type == 'password_input':
            elements.append(f'  <input type="password" class="{" ".join(classes)}" style="{style_str}" placeholder="{text or "Password"}">')
        elif block_type == 'button':
            elements.append(f'  <button class="{" ".join(classes)}" style="{style_str}">{text or "Button"}</button>')
        else:
            elements.append(f'  <div class="{" ".join(classes)}" style="{style_str}">{text or ""}</div>')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated UI</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
<div class="relative mx-auto bg-gray-100" style="width: {dims['width']}px; height: {dims['height']}px;">
{chr(10).join(elements)}
</div>
</body>
</html>'''
    
    return html


# ============================================================================
# React (Pixel-Perfect)
# ============================================================================

def generate_pixel_perfect_react(
    ils: Dict[str, Any],
    blocks: List[Dict[str, Any]]
) -> str:
    """Generate pixel-perfect React component."""
    logger.info("Generating pixel-perfect React component")
    
    dims = ils.get('image_dimensions', {'width': 1024, 'height': 768})
    
    elements = []
    
    for idx, block in enumerate(blocks):
        block_type = block.get('type', 'unknown')
        visual_style = block.get('visual_style', {})
        text = block.get('extracted_text', '')
        
        pos = visual_style.get('position', {})
        size = visual_style.get('size', {})
        colors = visual_style.get('colors', {})
        border_radius = visual_style.get('border_radius', 0)
        shadow = visual_style.get('shadow', {})
        padding = visual_style.get('padding', {})
        
        # Build React inline style object
        style_obj = {
            'position': 'absolute',
            'left': f"{pos.get('x', 0)}px",
            'top': f"{pos.get('y', 0)}px",
            'width': f"{size.get('width', 100)}px",
            'height': f"{size.get('height', 40)}px",
            'backgroundColor': colors.get('background', '#fff'),
            'color': colors.get('text', '#000'),
            'borderRadius': f"{border_radius}px",
            'padding': f"{padding.get('top', 8)}px {padding.get('right', 12)}px {padding.get('bottom', 8)}px {padding.get('left', 12)}px",
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'fontSize': f"{visual_style.get('font_size', 14)}px"
        }
        
        if shadow.get('has_shadow'):
            style_obj['boxShadow'] = f"0 {shadow.get('blur', 10)}px {shadow.get('spread', 2)}px {shadow.get('color', 'rgba(0,0,0,0.1)')}"
        
        style_str = '{' + ', '.join([f'{k}: "{v}"' if isinstance(v, str) else f'{k}: {v}' for k, v in style_obj.items()]) + '}'
        
        # Generate JSX element
        if block_type in ['text_input', 'input_field']:
            elements.append(f'      <input type="text" style={style_str} placeholder="{text or "Enter text"}" />')
        elif block_type == 'password_input':
            elements.append(f'      <input type="password" style={style_str} placeholder="{text or "Password"}" />')
        elif block_type == 'button':
            elements.append(f'      <button style={style_str}>{text or "Button"}</button>')
        else:
            elements.append(f'      <div style={style_str}>{text or ""}</div>')
    
    react_code = f'''import React from 'react';

export const GeneratedUI = () => {{
  return (
    <div 
      style={{{{
        position: 'relative',
        width: '{dims['width']}px',
        height: '{dims['height']}px',
        backgroundColor: '#f5f6fa',
        margin: '0 auto'
      }}}}
    >
{chr(10).join(elements)}
    </div>
  );
}};

export default GeneratedUI;
'''
    
    return react_code


# ============================================================================
# Flutter (Pixel-Perfect)
# ============================================================================

def generate_pixel_perfect_flutter(
    ils: Dict[str, Any],
    blocks: List[Dict[str, Any]]
) -> str:
    """Generate pixel-perfect Flutter code."""
    logger.info("Generating pixel-perfect Flutter code")
    
    dims = ils.get('image_dimensions', {'width': 1024, 'height': 768})
    
    widgets = []
    
    for idx, block in enumerate(blocks):
        block_type = block.get('type', 'unknown')
        visual_style = block.get('visual_style', {})
        text = block.get('extracted_text', '')
        
        pos = visual_style.get('position', {})
        size = visual_style.get('size', {})
        colors = visual_style.get('colors', {})
        border_radius = visual_style.get('border_radius', 0)
        
        # Parse hex colors
        bg_color = hex_to_flutter_color(colors.get('background', '#ffffff'))
        text_color = hex_to_flutter_color(colors.get('text', '#000000'))
        
        # Generate Flutter widget
        if block_type in ['text_input', 'input_field', 'password_input']:
            obscure = 'true' if block_type == 'password_input' else 'false'
            widgets.append(f'''        Positioned(
          left: {pos.get('x', 0)},
          top: {pos.get('y', 0)},
          width: {size.get('width', 100)},
          height: {size.get('height', 40)},
          child: TextField(
            obscureText: {obscure},
            decoration: InputDecoration(
              hintText: '{text or "Enter text"}',
              filled: true,
              fillColor: {bg_color},
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular({border_radius}),
                borderSide: BorderSide.none,
              ),
            ),
            style: TextStyle(color: {text_color}),
          ),
        ),''')
        elif block_type == 'button':
            widgets.append(f'''        Positioned(
          left: {pos.get('x', 0)},
          top: {pos.get('y', 0)},
          width: {size.get('width', 100)},
          height: {size.get('height', 40)},
          child: ElevatedButton(
            onPressed: () {{}},
            style: ElevatedButton.styleFrom(
              backgroundColor: {bg_color},
              foregroundColor: {text_color},
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular({border_radius}),
              ),
            ),
            child: Text('{text or "Button"}'),
          ),
        ),''')
        else:
            widgets.append(f'''        Positioned(
          left: {pos.get('x', 0)},
          top: {pos.get('y', 0)},
          width: {size.get('width', 100)},
          height: {size.get('height', 40)},
          child: Container(
            decoration: BoxDecoration(
              color: {bg_color},
              borderRadius: BorderRadius.circular({border_radius}),
            ),
            child: Center(
              child: Text(
                '{text or ""}',
                style: TextStyle(color: {text_color}),
              ),
            ),
          ),
        ),''')
    
    flutter_code = f'''import 'package:flutter/material.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {{
  const MyApp({{Key? key}}) : super(key: key);

  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      title: 'Generated UI',
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        body: Center(
          child: SizedBox(
            width: {dims['width']},
            height: {dims['height']},
            child: Stack(
              children: [
{chr(10).join(widgets)}
              ],
            ),
          ),
        ),
      ),
    );
  }}
}}
'''
    
    return flutter_code


def hex_to_flutter_color(hex_str: str) -> str:
    """Convert hex color to Flutter Color."""
    hex_str = hex_str.lstrip('#')
    return f"Color(0xFF{hex_str.upper()})"
