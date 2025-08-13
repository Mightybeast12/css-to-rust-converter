"""Rust code generation utilities for CSS to Rust conversion."""

import os
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template
from .parser import CssRule, CssKeyframe
from .mappings import ValueMappings


class RustGenerator:
    """Generates Rust code from parsed CSS rules."""

    def __init__(self, mappings: Optional[ValueMappings] = None):
        """Initialize the Rust generator."""
        self.mappings = mappings or ValueMappings()
        self.template_env = self._setup_templates()

    def _setup_templates(self) -> Environment:
        """Setup Jinja2 template environment."""
        # Get template directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(os.path.dirname(current_dir), 'templates')

        # Fallback to inline templates if directory doesn't exist
        if not os.path.exists(template_dir):
            return Environment()

        return Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate_style_function(self, function_name: str, rules: List[CssRule]) -> str:
        """Generate a single Rust style function from CSS rules."""
        css_content = self._combine_rules_to_css(rules)

        # Apply value mappings
        mapped_css = self._apply_mappings(css_content)

        # Generate function using template or inline
        try:
            template = self.template_env.get_template('style_function.rs.j2')
            return template.render(
                function_name=function_name,
                css_content=mapped_css,
                doc_comment=f"{function_name.replace('_', ' ').title()} styles"
            )
        except Exception:
            return self._generate_inline_function(function_name, mapped_css)

    def _generate_inline_function(self, function_name: str, css_content: str) -> str:
        """Generate Rust function using inline template."""
        doc_comment = f"{function_name.replace('_', ' ').title()} styles"

        return f'''//! {doc_comment}

use stylist::Style;

pub fn {function_name}() -> Style {{
    Style::new(
        r#"{css_content.strip()}
    "#,
    )
    .expect("Failed to create {function_name} styles")
}}'''

    def _combine_rules_to_css(self, rules: List[CssRule]) -> str:
        """Combine CSS rules back into CSS string."""
        css_parts = []

        # Group rules by media query
        regular_rules = []
        media_rules = {}

        for rule in rules:
            if rule.media_query:
                if rule.media_query not in media_rules:
                    media_rules[rule.media_query] = []
                media_rules[rule.media_query].append(rule)
            else:
                regular_rules.append(rule)

        # Add regular rules
        for rule in regular_rules:
            css_parts.append(self._rule_to_css_string(rule))

        # Add media query rules
        for media_query, media_rule_list in media_rules.items():
            css_parts.append(f"\n        @media {media_query} {{")
            for rule in media_rule_list:
                css_parts.append(self._rule_to_css_string(rule, indent="            "))
            css_parts.append("        }")

        return "\n".join(css_parts)

    def _rule_to_css_string(self, rule: CssRule, indent: str = "        ") -> str:
        """Convert a CSS rule back to CSS string."""
        properties_str = ""

        for prop_name, prop_value in rule.properties.items():
            properties_str += f"\n{indent}    {prop_name}: {prop_value};"

        if rule.pseudo_selector:
            selector = f"&:{rule.pseudo_selector}"
        else:
            selector = "&" if not rule.selector.startswith('.') else ""

        if properties_str:
            return f"{indent}{selector} {{{properties_str}\n{indent}}}"

        return ""

    def _apply_mappings(self, css_content: str) -> str:
        """Apply value mappings to CSS content."""
        lines = css_content.split('\n')
        mapped_lines = []

        for line in lines:
            # Skip non-property lines
            if ':' not in line or line.strip().startswith('@'):
                mapped_lines.append(line)
                continue

            # Extract property and value
            parts = line.split(':', 1)
            if len(parts) != 2:
                mapped_lines.append(line)
                continue

            prop_part = parts[0]
            value_part = parts[1].strip().rstrip(';')

            # Extract property name
            prop_name = prop_part.split()[-1] if prop_part.split() else ""

            # Map the value
            mapped_value = self.mappings.map_value(prop_name, value_part)

            # Reconstruct line
            mapped_line = f"{prop_part}: {mapped_value};"
            mapped_lines.append(mapped_line)

        return '\n'.join(mapped_lines)

    def generate_component_module(self, component_name: str, functions: Dict[str, str]) -> str:
        """Generate a complete Rust module for a component."""
        try:
            template = self.template_env.get_template('component.rs.j2')
            return template.render(
                component_name=component_name,
                functions=functions,
                doc_comment=f"{component_name.replace('_', ' ').title()} component styles"
            )
        except Exception:
            return self._generate_inline_component_module(component_name, functions)

    def _generate_inline_component_module(self, component_name: str, functions: Dict[str, str]) -> str:
        """Generate component module using inline template."""
        doc_comment = f"{component_name.replace('_', ' ').title()} component styles"

        module_content = f'''//! {doc_comment}

use stylist::Style;

'''

        for function_name, function_code in functions.items():
            # Extract just the function part (remove the header and import)
            function_lines = function_code.split('\n')
            function_start = -1

            for i, line in enumerate(function_lines):
                if line.startswith('pub fn '):
                    function_start = i
                    break

            if function_start >= 0:
                function_body = '\n'.join(function_lines[function_start:])
                module_content += f"{function_body}\n\n"

        return module_content.rstrip() + '\n'

    def generate_mod_file(self, components: List[str]) -> str:
        """Generate a mod.rs file for the components."""
        try:
            template = self.template_env.get_template('mod_file.rs.j2')
            return template.render(components=components)
        except Exception:
            return self._generate_inline_mod_file(components)

    def _generate_inline_mod_file(self, components: List[str]) -> str:
        """Generate mod.rs file using inline template."""
        mod_content = f'''//! Style modules

'''

        # Add module declarations
        for component in sorted(components):
            mod_content += f"pub mod {component};\n"

        mod_content += "\n// Re-export all component styles\n"

        # Add re-exports
        for component in sorted(components):
            mod_content += f"pub use {component}::*;\n"

        return mod_content

    def generate_keyframe_functions(self, keyframes: List[CssKeyframe]) -> Dict[str, str]:
        """Generate Rust functions for CSS keyframes."""
        functions = {}

        for keyframe in keyframes:
            function_name = f"animation_{keyframe.name.lower()}"
            css_content = self._keyframe_to_css_string(keyframe)
            mapped_css = self._apply_mappings(css_content)

            functions[function_name] = self._generate_inline_function(function_name, mapped_css)

        return functions

    def _keyframe_to_css_string(self, keyframe: CssKeyframe) -> str:
        """Convert keyframe to CSS string."""
        css_parts = [f"        @keyframes {keyframe.name} {{"]

        for percentage, properties in keyframe.keyframes.items():
            css_parts.append(f"            {percentage} {{")

            for prop_name, prop_value in properties.items():
                css_parts.append(f"                {prop_name}: {prop_value};")

            css_parts.append("            }")

        css_parts.append("        }")

        return "\n".join(css_parts)

    def format_rust_code(self, code: str) -> str:
        """Format Rust code (basic formatting)."""
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()

            # Decrease indent for closing braces
            if stripped.endswith('}') and not stripped.startswith('//'):
                indent_level = max(0, indent_level - 1)

            # Add indented line
            if stripped:
                formatted_lines.append('    ' * indent_level + stripped)
            else:
                formatted_lines.append('')

            # Increase indent for opening braces
            if stripped.endswith('{') and not stripped.startswith('//'):
                indent_level += 1

        return '\n'.join(formatted_lines)

    def generate_utility_functions(self, common_patterns: Dict[str, List[CssRule]]) -> Dict[str, str]:
        """Generate utility functions for common CSS patterns."""
        utilities = {}

        # Common utility patterns
        utility_patterns = {
            'flex_center': ['display: flex', 'align-items: center', 'justify-content: center'],
            'flex_column': ['display: flex', 'flex-direction: column'],
            'flex_row': ['display: flex', 'flex-direction: row'],
            'absolute_center': ['position: absolute', 'top: 50%', 'left: 50%', 'transform: translate(-50%, -50%)'],
            'full_width': ['width: 100%'],
            'full_height': ['height: 100%'],
            'hidden': ['display: none'],
            'visible': ['display: block'],
        }

        for util_name, properties in utility_patterns.items():
            css_content = '\n        '.join(f"{prop};" for prop in properties)
            mapped_css = self._apply_mappings(css_content)
            utilities[util_name] = self._generate_inline_function(util_name, mapped_css)

        return utilities

    def create_file_structure(self, output_dir: str, components: Dict[str, Dict[str, str]]):
        """Create the complete file structure in the output directory."""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate component files
        component_names = []
        for component_name, functions in components.items():
            component_names.append(component_name)

            # Generate component module
            module_content = self.generate_component_module(component_name, functions)

            # Write component file
            component_file = os.path.join(output_dir, f"{component_name}.rs")
            with open(component_file, 'w', encoding='utf-8') as f:
                f.write(module_content)

        # Generate mod.rs file
        mod_content = self.generate_mod_file(component_names)
        mod_file = os.path.join(output_dir, "mod.rs")
        with open(mod_file, 'w', encoding='utf-8') as f:
            f.write(mod_content)

        return component_names
