"""Utility functions for CSS to Rust conversion."""

import re
from typing import List, Dict, Any, Optional


def normalize_selector(selector: str) -> str:
    """Normalize CSS selector for consistent processing."""
    # Remove extra whitespace
    selector = re.sub(r'\s+', ' ', selector.strip())

    # Normalize pseudo-selectors
    selector = re.sub(r'\s*:\s*', ':', selector)

    return selector


def extract_class_name(selector: str) -> Optional[str]:
    """Extract the main class name from a CSS selector."""
    # Remove pseudo-selectors first
    base_selector = selector.split(':')[0].strip()

    # Extract class name (remove leading dot)
    if base_selector.startswith('.'):
        return base_selector[1:]

    # Handle ID selectors
    if base_selector.startswith('#'):
        return base_selector[1:]

    # Handle element selectors
    if ' ' not in base_selector and '.' not in base_selector:
        return base_selector

    return None


def is_valid_rust_identifier(name: str) -> bool:
    """Check if a string is a valid Rust identifier."""
    if not name:
        return False

    # Must start with letter or underscore
    if not (name[0].isalpha() or name[0] == '_'):
        return False

    # Can contain letters, digits, underscores
    return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None


def sanitize_rust_identifier(name: str) -> str:
    """Convert a string to a valid Rust identifier."""
    if not name:
        return 'style'

    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)

    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)

    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')

    # Ensure it starts with a letter or underscore
    if sanitized and not (sanitized[0].isalpha() or sanitized[0] == '_'):
        sanitized = f'style_{sanitized}'

    # Handle empty result
    if not sanitized:
        sanitized = 'style'

    # Handle Rust keywords
    rust_keywords = {
        'as', 'break', 'const', 'continue', 'crate', 'else', 'enum', 'extern',
        'false', 'fn', 'for', 'if', 'impl', 'in', 'let', 'loop', 'match',
        'mod', 'move', 'mut', 'pub', 'ref', 'return', 'self', 'Self',
        'static', 'struct', 'super', 'trait', 'true', 'type', 'unsafe',
        'use', 'where', 'while', 'async', 'await', 'dyn'
    }

    if sanitized in rust_keywords:
        sanitized = f'{sanitized}_style'

    return sanitized


def format_css_property(property_name: str, property_value: str) -> str:
    """Format a CSS property for inclusion in Rust code."""
    # Normalize property name
    property_name = property_name.strip()

    # Normalize property value
    property_value = property_value.strip().rstrip(';')

    return f"{property_name}: {property_value};"


def detect_css_framework(css_content: str) -> Optional[str]:
    """Detect which CSS framework is being used."""
    css_lower = css_content.lower()

    # Bootstrap detection
    if any(keyword in css_lower for keyword in ['bootstrap', 'btn-', 'card-', 'navbar-']):
        return 'bootstrap'

    # Tailwind detection
    if any(keyword in css_lower for keyword in ['@tailwind', 'tailwind', 'prose-']):
        return 'tailwind'

    # Bulma detection
    if any(keyword in css_lower for keyword in ['bulma', 'is-primary', 'has-']):
        return 'bulma'

    # Foundation detection
    if any(keyword in css_lower for keyword in ['foundation', 'callout', 'orbit']):
        return 'foundation'

    return None


def estimate_conversion_complexity(css_content: str) -> Dict[str, Any]:
    """Estimate the complexity of converting the CSS."""
    lines = css_content.split('\n')

    complexity = {
        'total_lines': len(lines),
        'rules_count': len(re.findall(r'\{[^}]*\}', css_content)),
        'media_queries': len(re.findall(r'@media[^{]*\{', css_content)),
        'keyframes': len(re.findall(r'@keyframes[^{]*\{', css_content)),
        'pseudo_selectors': len(re.findall(r':[a-zA-Z-]+', css_content)),
        'calc_functions': len(re.findall(r'calc\([^)]*\)', css_content)),
        'css_variables': len(re.findall(r'var\([^)]*\)', css_content)),
        'complex_selectors': len(re.findall(r'[^{]*\s+[^{]*\{', css_content)),
    }

    # Estimate difficulty level
    total_complexity = (
        complexity['rules_count'] * 1 +
        complexity['media_queries'] * 2 +
        complexity['keyframes'] * 3 +
        complexity['pseudo_selectors'] * 0.5 +
        complexity['calc_functions'] * 2 +
        complexity['complex_selectors'] * 1.5
    )

    if total_complexity < 10:
        complexity['difficulty'] = 'easy'
    elif total_complexity < 50:
        complexity['difficulty'] = 'medium'
    else:
        complexity['difficulty'] = 'hard'

    return complexity


def group_related_selectors(selectors: List[str]) -> Dict[str, List[str]]:
    """Group related CSS selectors together."""
    groups = {}

    for selector in selectors:
        # Extract base name
        base_name = extract_class_name(selector)
        if not base_name:
            continue

        # Find the root component name
        root_name = base_name.split('-')[0] if '-' in base_name else base_name

        if root_name not in groups:
            groups[root_name] = []

        groups[root_name].append(selector)

    return groups


def optimize_css_content(css_content: str) -> str:
    """Optimize CSS content for better conversion."""
    # Remove comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)

    # Remove empty lines
    lines = [line.strip() for line in css_content.split('\n') if line.strip()]

    # Remove duplicate whitespace
    css_content = '\n'.join(lines)
    css_content = re.sub(r'\s+', ' ', css_content)

    # Normalize brackets
    css_content = re.sub(r'\s*{\s*', ' {\n    ', css_content)
    css_content = re.sub(r'\s*}\s*', '\n}\n', css_content)
    css_content = re.sub(r';\s*', ';\n    ', css_content)

    return css_content


def validate_css_syntax(css_content: str) -> List[str]:
    """Basic CSS syntax validation."""
    errors = []

    # Check for balanced brackets
    open_braces = css_content.count('{')
    close_braces = css_content.count('}')

    if open_braces != close_braces:
        errors.append(f"Unbalanced braces: {open_braces} opening, {close_braces} closing")

    # Check for empty selectors
    empty_selectors = re.findall(r'\s*\{\s*\}', css_content)
    if empty_selectors:
        errors.append(f"Found {len(empty_selectors)} empty rule(s)")

    # Check for invalid property syntax
    lines = css_content.split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line and ':' in line and not line.startswith('@') and not line.endswith('{') and not line.endswith('}'):
            if not line.endswith(';'):
                errors.append(f"Line {i}: Missing semicolon - '{line}'")

    return errors


def extract_color_palette(css_content: str) -> Dict[str, List[str]]:
    """Extract color palette from CSS content."""
    colors = {
        'hex': re.findall(r'#[0-9a-fA-F]{3,6}', css_content),
        'rgb': re.findall(r'rgb\([^)]+\)', css_content),
        'rgba': re.findall(r'rgba\([^)]+\)', css_content),
        'hsl': re.findall(r'hsl\([^)]+\)', css_content),
        'hsla': re.findall(r'hsla\([^)]+\)', css_content),
        'named': []
    }

    # Named colors
    named_colors = [
        'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'brown',
        'black', 'white', 'gray', 'grey', 'cyan', 'magenta', 'lime', 'maroon',
        'navy', 'olive', 'silver', 'teal', 'aqua', 'fuchsia'
    ]

    for color in named_colors:
        if re.search(rf'\b{color}\b', css_content, re.IGNORECASE):
            colors['named'].append(color)

    # Remove duplicates
    for color_type in colors:
        colors[color_type] = list(set(colors[color_type]))

    return colors


def calculate_specificity(selector: str) -> int:
    """Calculate CSS selector specificity."""
    # Simple specificity calculation
    # IDs = 100, Classes/Attributes/Pseudo-classes = 10, Elements/Pseudo-elements = 1

    specificity = 0

    # Count IDs
    specificity += selector.count('#') * 100

    # Count classes, attributes, and pseudo-classes
    specificity += len(re.findall(r'\.[\w-]+', selector)) * 10  # Classes
    specificity += len(re.findall(r'\[[^\]]+\]', selector)) * 10  # Attributes
    specificity += len(re.findall(r':[\w-]+', selector)) * 10  # Pseudo-classes

    # Count elements and pseudo-elements
    elements = re.findall(r'\b[a-zA-Z][\w-]*(?![#\.\[:])', selector)
    specificity += len(elements) * 1

    return specificity
