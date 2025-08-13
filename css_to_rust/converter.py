"""Main CSS to Rust converter class."""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from .parser import CssParser, CssRule, CssKeyframe
from .generator import RustGenerator
from .mappings import ValueMappings


class CssToRustConverter:
    """Main converter class that orchestrates CSS to Rust conversion."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the converter with optional configuration."""
        self.mappings = ValueMappings(config_path)
        self.parser = CssParser()
        self.generator = RustGenerator(self.mappings)

    def convert_file(self, input_path: str, output_path: str, **options) -> Dict[str, Any]:
        """Convert a single CSS file to Rust."""
        # Read CSS file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"CSS file not found: {input_path}")
        except Exception as e:
            raise Exception(f"Error reading CSS file {input_path}: {e}")

        # Parse CSS
        rules = self.parser.parse(css_content)
        keyframes = self.parser.keyframes

        # Group rules if requested
        if options.get('group_by_component', False):
            components = self.parser.group_rules_by_component(rules)
            return self._convert_components(components, keyframes, output_path, **options)
        else:
            return self._convert_single_file(rules, keyframes, output_path, **options)

    def convert_directory(self, input_dir: str, output_dir: str, **options) -> Dict[str, Any]:
        """Convert all CSS files in a directory."""
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        results = {}
        css_files = list(input_path.glob("*.css"))

        if not css_files:
            print(f"No CSS files found in {input_dir}")
            return results

        for css_file in css_files:
            try:
                print(f"Converting {css_file.name}...")
                output_file = output_path / f"{css_file.stem}.rs"
                result = self.convert_file(str(css_file), str(output_file), **options)
                results[css_file.name] = result
            except Exception as e:
                print(f"Error converting {css_file.name}: {e}")
                results[css_file.name] = {"error": str(e)}

        return results

    def _convert_single_file(self, rules: List[CssRule], keyframes: List[CssKeyframe],
                           output_path: str, **options) -> Dict[str, Any]:
        """Convert rules to a single Rust file."""
        functions = {}

        # Generate functions from rules
        if options.get('extract_variants', True):
            variants = self.parser.extract_variants(rules)
            for variant_name, variant_rules in variants.items():
                function_name = self.parser.get_function_name_from_selector(variant_name)
                functions[function_name] = self.generator.generate_style_function(
                    function_name, variant_rules
                )
        else:
            # Group by selector
            grouped_rules = {}
            for rule in rules:
                func_name = self.parser.get_function_name_from_selector(
                    rule.selector, rule.pseudo_selector
                )
                if func_name not in grouped_rules:
                    grouped_rules[func_name] = []
                grouped_rules[func_name].append(rule)

            for func_name, func_rules in grouped_rules.items():
                functions[func_name] = self.generator.generate_style_function(
                    func_name, func_rules
                )

        # Generate keyframe functions
        if keyframes:
            keyframe_functions = self.generator.generate_keyframe_functions(keyframes)
            functions.update(keyframe_functions)

        # Generate utilities if requested
        if options.get('include_utilities', False):
            utilities = self.generator.generate_utility_functions({})
            functions.update(utilities)

        # Write single file
        self._write_single_rust_file(output_path, functions)

        return {
            "type": "single_file",
            "output": output_path,
            "functions": list(functions.keys()),
            "keyframes": len(keyframes)
        }

    def _convert_components(self, components: Dict[str, List[CssRule]],
                          keyframes: List[CssKeyframe], output_path: str,
                          **options) -> Dict[str, Any]:
        """Convert rules grouped by components."""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        component_functions = {}

        # Process each component
        for component_name, component_rules in components.items():
            functions = {}

            # Extract variants for this component
            if options.get('extract_variants', True):
                variants = self.parser.extract_variants(component_rules)
                for variant_name, variant_rules in variants.items():
                    function_name = self.parser.get_function_name_from_selector(variant_name)
                    functions[function_name] = self.generator.generate_style_function(
                        function_name, variant_rules
                    )
            else:
                # Group by selector within component
                grouped_rules = {}
                for rule in component_rules:
                    func_name = self.parser.get_function_name_from_selector(
                        rule.selector, rule.pseudo_selector
                    )
                    if func_name not in grouped_rules:
                        grouped_rules[func_name] = []
                    grouped_rules[func_name].append(rule)

                for func_name, func_rules in grouped_rules.items():
                    functions[func_name] = self.generator.generate_style_function(
                        func_name, func_rules
                    )

            component_functions[component_name] = functions

        # Add keyframes to appropriate component or create separate module
        if keyframes:
            keyframe_functions = self.generator.generate_keyframe_functions(keyframes)
            if 'animations' not in component_functions:
                component_functions['animations'] = {}
            component_functions['animations'].update(keyframe_functions)

        # Generate utilities if requested
        if options.get('include_utilities', False):
            utilities = self.generator.generate_utility_functions({})
            component_functions['utils'] = utilities

        # Create file structure
        created_components = self.generator.create_file_structure(
            str(output_dir), component_functions
        )

        return {
            "type": "component_structure",
            "output": str(output_dir),
            "components": created_components,
            "functions": sum(len(funcs) for funcs in component_functions.values()),
            "keyframes": len(keyframes)
        }

    def _write_single_rust_file(self, output_path: str, functions: Dict[str, str]):
        """Write all functions to a single Rust file."""
        file_content = "//! Generated CSS styles\n\nuse stylist::Style;\n\n"

        for function_name, function_code in functions.items():
            # Extract just the function part
            function_lines = function_code.split('\n')
            function_start = -1

            for i, line in enumerate(function_lines):
                if line.startswith('pub fn '):
                    function_start = i
                    break

            if function_start >= 0:
                function_body = '\n'.join(function_lines[function_start:])
                file_content += f"{function_body}\n\n"

        # Write to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(file_content.rstrip() + '\n')

    def convert_string(self, css_content: str, **options) -> Dict[str, str]:
        """Convert CSS string directly to Rust functions."""
        # Parse CSS
        rules = self.parser.parse(css_content)
        keyframes = self.parser.keyframes

        functions = {}

        # Generate functions from rules
        if options.get('extract_variants', True):
            variants = self.parser.extract_variants(rules)
            for variant_name, variant_rules in variants.items():
                function_name = self.parser.get_function_name_from_selector(variant_name)
                functions[function_name] = self.generator.generate_style_function(
                    function_name, variant_rules
                )
        else:
            # Group by selector
            grouped_rules = {}
            for rule in rules:
                func_name = self.parser.get_function_name_from_selector(
                    rule.selector, rule.pseudo_selector
                )
                if func_name not in grouped_rules:
                    grouped_rules[func_name] = []
                grouped_rules[func_name].append(rule)

            for func_name, func_rules in grouped_rules.items():
                functions[func_name] = self.generator.generate_style_function(
                    func_name, func_rules
                )

        # Generate keyframe functions
        if keyframes:
            keyframe_functions = self.generator.generate_keyframe_functions(keyframes)
            functions.update(keyframe_functions)

        return functions

    def analyze_css(self, css_content: str) -> Dict[str, Any]:
        """Analyze CSS content and return statistics."""
        rules = self.parser.parse(css_content)
        keyframes = self.parser.keyframes

        # Basic statistics
        stats = {
            "total_rules": len(rules),
            "total_keyframes": len(keyframes),
            "media_queries": len([r for r in rules if r.media_query]),
            "pseudo_selectors": len([r for r in rules if r.pseudo_selector]),
        }

        # Analyze selectors
        selectors = [rule.selector for rule in rules]
        stats["unique_selectors"] = len(set(selectors))

        # Analyze properties
        all_properties = []
        for rule in rules:
            all_properties.extend(rule.properties.keys())

        stats["total_properties"] = len(all_properties)
        stats["unique_properties"] = len(set(all_properties))

        # Component analysis
        components = self.parser.group_rules_by_component(rules)
        stats["components"] = {
            name: len(component_rules)
            for name, component_rules in components.items()
        }

        # Value analysis
        all_values = []
        for rule in rules:
            all_values.extend(rule.properties.values())

        # Check how many values can be mapped
        mappable_values = 0
        for value in all_values:
            for prop_name in rule.properties.keys():
                if self.mappings.map_value(prop_name, value) != value:
                    mappable_values += 1
                    break

        stats["mappable_values"] = mappable_values
        stats["mapping_coverage"] = f"{(mappable_values / len(all_values) * 100):.1f}%" if all_values else "0%"

        return stats

    def get_conversion_options(self) -> Dict[str, Any]:
        """Get available conversion options."""
        return {
            "group_by_component": {
                "description": "Group CSS rules by component and create separate files",
                "default": False,
                "type": "boolean"
            },
            "extract_variants": {
                "description": "Extract style variants (e.g., btn-primary, btn-secondary)",
                "default": True,
                "type": "boolean"
            },
            "include_utilities": {
                "description": "Include common utility functions",
                "default": False,
                "type": "boolean"
            },
            "apply_mappings": {
                "description": "Apply value mappings to CSS variables",
                "default": True,
                "type": "boolean"
            }
        }

    def validate_css(self, css_content: str) -> List[str]:
        """Validate CSS content and return any warnings or errors."""
        warnings = []

        try:
            rules = self.parser.parse(css_content)
        except Exception as e:
            warnings.append(f"CSS parsing error: {e}")
            return warnings

        # Check for common issues
        for rule in rules:
            # Check for empty rules
            if not rule.properties:
                warnings.append(f"Empty rule found: {rule.selector}")

            # Check for potentially problematic selectors
            if ' ' in rule.selector and not rule.selector.startswith('.'):
                warnings.append(f"Complex selector may not convert well: {rule.selector}")

            # Check for unsupported CSS features
            for prop_name, prop_value in rule.properties.items():
                if 'calc(' in prop_value:
                    warnings.append(f"CSS calc() function found in {rule.selector}.{prop_name}")

                if 'var(' in prop_value and not prop_value.startswith('var(--'):
                    warnings.append(f"Non-standard CSS variable in {rule.selector}.{prop_name}")

        return warnings
