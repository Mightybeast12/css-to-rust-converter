"""CSS parsing utilities for converting CSS to Rust."""

import re
import cssutils
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CssRule:
    """Represents a parsed CSS rule."""
    selector: str
    properties: Dict[str, str]
    media_query: Optional[str] = None
    pseudo_selector: Optional[str] = None
    raw_css: str = ""


@dataclass
class CssKeyframe:
    """Represents a CSS keyframe animation."""
    name: str
    keyframes: Dict[str, Dict[str, str]]


class CssParser:
    """Parses CSS into structured data for conversion to Rust."""

    def __init__(self):
        """Initialize the CSS parser."""
        self.rules: List[CssRule] = []
        self.keyframes: List[CssKeyframe] = []
        self.imports: List[str] = []

    def parse(self, css_content: str) -> List[CssRule]:
        """Parse CSS content and return structured rules."""
        self.rules = []
        self.keyframes = []
        self.imports = []

        try:
            # Try using cssutils for robust parsing
            return self._parse_with_cssutils(css_content)
        except Exception as e:
            print(f"Warning: cssutils parsing failed ({e}), falling back to regex parsing")
            return self._parse_with_regex(css_content)

    def _parse_with_cssutils(self, css_content: str) -> List[CssRule]:
        """Parse CSS using the cssutils library."""
        # Suppress cssutils warnings
        cssutils.log.setLevel('ERROR')

        sheet = cssutils.parseString(css_content)
        rules = []

        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                css_rule = self._parse_style_rule(rule)
                if css_rule:
                    rules.append(css_rule)
            elif rule.type == rule.MEDIA_RULE:
                media_rules = self._parse_media_rule(rule)
                rules.extend(media_rules)
            elif rule.type == rule.KEYFRAMES_RULE:
                keyframe = self._parse_keyframes_rule(rule)
                if keyframe:
                    self.keyframes.append(keyframe)
            elif rule.type == rule.IMPORT_RULE:
                self.imports.append(rule.href)

        return rules

    def _parse_style_rule(self, rule) -> Optional[CssRule]:
        """Parse a CSS style rule."""
        try:
            selector = rule.selectorText.strip()
            properties = {}

            for prop in rule.style:
                name = prop.name
                value = prop.value
                if name and value:
                    properties[name] = value

            if not properties:
                return None

            # Extract pseudo-selector if present
            pseudo_selector = None
            if ':' in selector and not selector.startswith(':root'):
                parts = selector.split(':', 1)
                if len(parts) == 2:
                    selector = parts[0].strip()
                    pseudo_selector = parts[1].strip()

            return CssRule(
                selector=selector,
                properties=properties,
                pseudo_selector=pseudo_selector,
                raw_css=rule.cssText
            )
        except Exception as e:
            print(f"Warning: Failed to parse style rule: {e}")
            return None

    def _parse_media_rule(self, rule) -> List[CssRule]:
        """Parse a CSS media rule."""
        media_query = rule.media.mediaText
        rules = []

        for nested_rule in rule:
            if nested_rule.type == nested_rule.STYLE_RULE:
                css_rule = self._parse_style_rule(nested_rule)
                if css_rule:
                    css_rule.media_query = media_query
                    rules.append(css_rule)

        return rules

    def _parse_keyframes_rule(self, rule) -> Optional[CssKeyframe]:
        """Parse a CSS keyframes rule."""
        try:
            name = rule.name
            keyframes = {}

            for keyframe_rule in rule:
                key = keyframe_rule.keyText
                properties = {}

                for prop in keyframe_rule.style:
                    properties[prop.name] = prop.value

                if properties:
                    keyframes[key] = properties

            return CssKeyframe(name=name, keyframes=keyframes)
        except Exception as e:
            print(f"Warning: Failed to parse keyframes rule: {e}")
            return None

    def _parse_with_regex(self, css_content: str) -> List[CssRule]:
        """Fallback CSS parsing using regex."""
        rules = []

        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)

        # Extract media queries
        media_pattern = r'@media\s+([^{]+)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        media_matches = re.findall(media_pattern, css_content, re.DOTALL)

        for media_query, media_content in media_matches:
            media_rules = self._parse_rules_content(media_content.strip(), media_query.strip())
            rules.extend(media_rules)
            # Remove processed media query from content
            css_content = css_content.replace(f'@media {media_query} {{{media_content}}}', '')

        # Extract keyframes
        keyframe_pattern = r'@keyframes\s+([^{]+)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        keyframe_matches = re.findall(keyframe_pattern, css_content, re.DOTALL)

        for name, keyframe_content in keyframe_matches:
            self._parse_keyframes_content(name.strip(), keyframe_content.strip())
            # Remove processed keyframes from content
            css_content = css_content.replace(f'@keyframes {name} {{{keyframe_content}}}', '')

        # Parse regular rules
        regular_rules = self._parse_rules_content(css_content)
        rules.extend(regular_rules)

        return rules

    def _parse_rules_content(self, content: str, media_query: Optional[str] = None) -> List[CssRule]:
        """Parse CSS rules from content string."""
        rules = []

        # Pattern to match CSS rules: selector { properties }
        rule_pattern = r'([^{]+)\{([^}]+)\}'
        rule_matches = re.findall(rule_pattern, content)

        for selector, properties_str in rule_matches:
            selector = selector.strip()
            if not selector:
                continue

            properties = self._parse_properties_string(properties_str)
            if not properties:
                continue

            # Extract pseudo-selector
            pseudo_selector = None
            if ':' in selector and not selector.startswith(':root'):
                parts = selector.split(':', 1)
                if len(parts) == 2:
                    selector = parts[0].strip()
                    pseudo_selector = parts[1].strip()

            rule = CssRule(
                selector=selector,
                properties=properties,
                media_query=media_query,
                pseudo_selector=pseudo_selector,
                raw_css=f"{selector} {{ {properties_str} }}"
            )
            rules.append(rule)

        return rules

    def _parse_properties_string(self, properties_str: str) -> Dict[str, str]:
        """Parse CSS properties from a string."""
        properties = {}

        # Split by semicolon and parse each property
        for prop_str in properties_str.split(';'):
            prop_str = prop_str.strip()
            if not prop_str:
                continue

            if ':' in prop_str:
                name, value = prop_str.split(':', 1)
                name = name.strip()
                value = value.strip()

                if name and value:
                    properties[name] = value

        return properties

    def _parse_keyframes_content(self, name: str, content: str):
        """Parse keyframes content."""
        keyframes = {}

        # Pattern to match keyframe rules: percentage { properties }
        keyframe_pattern = r'([^{]+)\{([^}]+)\}'
        keyframe_matches = re.findall(keyframe_pattern, content)

        for key, properties_str in keyframe_matches:
            key = key.strip()
            properties = self._parse_properties_string(properties_str)

            if properties:
                keyframes[key] = properties

        if keyframes:
            self.keyframes.append(CssKeyframe(name=name, keyframes=keyframes))

    def group_rules_by_component(self, rules: List[CssRule]) -> Dict[str, List[CssRule]]:
        """Group CSS rules by component based on selector patterns."""
        components = {}

        for rule in rules:
            component_name = self._extract_component_name(rule.selector)

            if component_name not in components:
                components[component_name] = []

            components[component_name].append(rule)

        return components

    def _extract_component_name(self, selector: str) -> str:
        """Extract component name from CSS selector."""
        # Remove leading dots and spaces
        selector = selector.lstrip('. ')

        # Common component patterns
        if selector.startswith('btn'):
            return 'button'
        elif selector.startswith('card'):
            return 'card'
        elif selector.startswith('nav'):
            return 'navbar'
        elif selector.startswith('modal'):
            return 'modal'
        elif selector.startswith('form'):
            return 'form'
        elif selector.startswith('input'):
            return 'input'
        elif selector.startswith('table'):
            return 'table'
        elif selector.startswith('alert'):
            return 'alert'

        # Extract first word as component name
        words = re.split(r'[-_\s]', selector)
        if words:
            return words[0].lower()

        return 'component'

    def get_function_name_from_selector(self, selector: str, pseudo_selector: Optional[str] = None) -> str:
        """Generate a Rust function name from CSS selector."""
        # Clean selector
        name = selector.replace('.', '').replace('#', '').replace(' ', '_')
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        name = re.sub(r'_+', '_', name).strip('_')

        # Add pseudo selector if present
        if pseudo_selector:
            pseudo_clean = re.sub(r'[^a-zA-Z0-9_]', '_', pseudo_selector)
            name = f"{name}_{pseudo_clean}"

        # Ensure it starts with a letter or underscore
        if name and not (name[0].isalpha() or name[0] == '_'):
            name = f"style_{name}"

        return name.lower() if name else 'style'

    def extract_variants(self, rules: List[CssRule]) -> Dict[str, List[CssRule]]:
        """Extract style variants from rules (e.g., btn-primary, btn-secondary)."""
        variants = {}

        for rule in rules:
            base_name, variant_name = self._split_variant_name(rule.selector)

            if variant_name:
                key = f"{base_name}_{variant_name}"
            else:
                key = base_name

            if key not in variants:
                variants[key] = []

            variants[key].append(rule)

        return variants

    def _split_variant_name(self, selector: str) -> Tuple[str, Optional[str]]:
        """Split selector into base name and variant name."""
        # Remove leading dots and clean
        clean_selector = selector.lstrip('. ')

        # Common variant patterns
        variant_patterns = [
            r'([a-zA-Z]+)[-_](primary|secondary|success|danger|warning|info|light|dark)',
            r'([a-zA-Z]+)[-_](small|sm|large|lg|xl|xs)',
            r'([a-zA-Z]+)[-_](outline|solid|ghost|link)',
            r'([a-zA-Z]+)[-_]([a-zA-Z]+)'
        ]

        for pattern in variant_patterns:
            match = re.match(pattern, clean_selector, re.IGNORECASE)
            if match:
                return match.group(1).lower(), match.group(2).lower()

        return clean_selector.lower(), None
