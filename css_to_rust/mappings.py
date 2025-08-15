"""Value mappings for CSS to Rust conversion."""

import json
import os
from typing import Any, Dict, Optional


class ValueMappings:
    """Handles mapping CSS values to Rust/theme equivalents."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize with default or custom mappings."""
        self.mappings = self._load_default_mappings()

        if config_path and os.path.exists(config_path):
            custom_mappings = self._load_custom_mappings(config_path)
            self._merge_mappings(custom_mappings)

    def _load_default_mappings(self) -> Dict[str, Any]:
        """Load default CSS to Rust mappings."""
        return {
            "colors": {
                # Primary colors
                "#007bff": "var(--color-primary)",
                "#0056b3": "var(--color-primary-hover)",
                "#004085": "var(--color-primary-active)",
                # Secondary colors
                "#6c757d": "var(--color-secondary)",
                "#545b62": "var(--color-secondary-hover)",
                "#4e555b": "var(--color-secondary-active)",
                # Success colors
                "#28a745": "var(--color-success)",
                "#1e7e34": "var(--color-success-hover)",
                # Danger colors
                "#dc3545": "var(--color-error)",
                "#c82333": "var(--color-error-hover)",
                # Warning colors
                "#ffc107": "var(--color-warning)",
                "#e0a800": "var(--color-warning-hover)",
                # Text colors
                "#212529": "var(--color-text-primary)",
                "#6c757d": "var(--color-text-secondary)",
                "#adb5bd": "var(--color-text-muted)",
                "#ffffff": "var(--color-text-on-primary)",
                # Background colors
                "#ffffff": "var(--color-background)",
                "#f8f9fa": "var(--color-surface)",
                "#e9ecef": "var(--color-surface-hover)",
                # Border colors
                "#dee2e6": "var(--color-border)",
                "#adb5bd": "var(--color-border-hover)",
                # Common shorthands
                "white": "var(--color-background)",
                "black": "var(--color-text-primary)",
                "transparent": "transparent",
            },
            "spacing": {
                # Pixel values
                "2px": "var(--spacing-xs)",
                "4px": "var(--spacing-xs)",
                "8px": "var(--spacing-sm)",
                "12px": "var(--spacing-md)",
                "16px": "var(--spacing-md)",
                "20px": "var(--spacing-lg)",
                "24px": "var(--spacing-lg)",
                "32px": "var(--spacing-xl)",
                "40px": "var(--spacing-xxl)",
                "48px": "var(--spacing-xxl)",
                # REM values
                "0.125rem": "var(--spacing-xs)",
                "0.25rem": "var(--spacing-xs)",
                "0.5rem": "var(--spacing-sm)",
                "0.75rem": "var(--spacing-md)",
                "1rem": "var(--spacing-md)",
                "1.25rem": "var(--spacing-lg)",
                "1.5rem": "var(--spacing-lg)",
                "2rem": "var(--spacing-xl)",
                "2.5rem": "var(--spacing-xxl)",
                "3rem": "var(--spacing-xxl)",
            },
            "border_radius": {
                "2px": "var(--border-radius-sm)",
                "4px": "var(--border-radius-sm)",
                "6px": "var(--border-radius-md)",
                "8px": "var(--border-radius-md)",
                "12px": "var(--border-radius-lg)",
                "16px": "var(--border-radius-lg)",
                "50%": "50%",
                "9999px": "var(--border-radius-full)",
                "0.125rem": "var(--border-radius-sm)",
                "0.25rem": "var(--border-radius-sm)",
                "0.375rem": "var(--border-radius-md)",
                "0.5rem": "var(--border-radius-md)",
                "0.75rem": "var(--border-radius-lg)",
                "1rem": "var(--border-radius-lg)",
            },
            "font_sizes": {
                "12px": "var(--font-size-xs)",
                "14px": "var(--font-size-sm)",
                "16px": "var(--font-size-md)",
                "18px": "var(--font-size-lg)",
                "20px": "var(--font-size-xl)",
                "24px": "var(--font-size-xxl)",
                "0.75rem": "var(--font-size-xs)",
                "0.875rem": "var(--font-size-sm)",
                "1rem": "var(--font-size-md)",
                "1.125rem": "var(--font-size-lg)",
                "1.25rem": "var(--font-size-xl)",
                "1.5rem": "var(--font-size-xxl)",
            },
            "font_weights": {
                "300": "var(--font-weight-light)",
                "400": "var(--font-weight-normal)",
                "500": "var(--font-weight-medium)",
                "600": "var(--font-weight-semibold)",
                "700": "var(--font-weight-bold)",
                "800": "var(--font-weight-extrabold)",
                "light": "var(--font-weight-light)",
                "normal": "var(--font-weight-normal)",
                "medium": "var(--font-weight-medium)",
                "semibold": "var(--font-weight-semibold)",
                "bold": "var(--font-weight-bold)",
            },
            "shadows": {
                "0 1px 3px rgba(0,0,0,0.1)": "var(--shadow-sm)",
                "0 4px 6px rgba(0,0,0,0.1)": "var(--shadow-md)",
                "0 10px 15px rgba(0,0,0,0.1)": "var(--shadow-lg)",
                "0 20px 25px rgba(0,0,0,0.1)": "var(--shadow-xl)",
                "none": "none",
            },
            "transitions": {
                "0.15s": "var(--transition-fast)",
                "0.2s": "var(--transition-fast)",
                "0.3s": "var(--transition-normal)",
                "0.5s": "var(--transition-slow)",
                "150ms": "var(--transition-fast)",
                "200ms": "var(--transition-fast)",
                "300ms": "var(--transition-normal)",
                "500ms": "var(--transition-slow)",
            },
            "breakpoints": {
                "576px": "var(--breakpoint-sm)",
                "768px": "var(--breakpoint-md)",
                "992px": "var(--breakpoint-lg)",
                "1200px": "var(--breakpoint-xl)",
                "1400px": "var(--breakpoint-xxl)",
            },
        }

    def _load_custom_mappings(self, config_path: str) -> Dict[str, Any]:
        """Load custom mappings from JSON file."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load custom mappings from {config_path}: {e}")
            return {}

    def _merge_mappings(self, custom_mappings: Dict[str, Any]):
        """Merge custom mappings with defaults."""
        for category, values in custom_mappings.items():
            if category in self.mappings:
                self.mappings[category].update(values)
            else:
                self.mappings[category] = values

    def map_value(self, property_name: str, value: str) -> str:
        """Map a CSS value to its Rust equivalent."""
        # Normalize the value
        value = value.strip()

        # Determine the category based on property name
        category = self._get_category_for_property(property_name)

        if category and category in self.mappings:
            return self.mappings[category].get(value, value)

        # Check all categories if no specific category found
        for cat_values in self.mappings.values():
            if isinstance(cat_values, dict) and value in cat_values:
                return cat_values[value]

        return value

    def _get_category_for_property(self, property_name: str) -> Optional[str]:
        """Determine which mapping category to use for a CSS property."""
        property_name = property_name.lower()

        if any(keyword in property_name for keyword in ["color", "background"]):
            return "colors"
        elif any(
            keyword in property_name
            for keyword in ["padding", "margin", "gap", "spacing"]
        ):
            return "spacing"
        elif "border-radius" in property_name or property_name == "border-radius":
            return "border_radius"
        elif "font-size" in property_name:
            return "font_sizes"
        elif "font-weight" in property_name:
            return "font_weights"
        elif "box-shadow" in property_name or "shadow" in property_name:
            return "shadows"
        elif "transition" in property_name:
            return "transitions"
        elif any(
            keyword in property_name for keyword in ["width", "max-width", "min-width"]
        ):
            return "breakpoints"

        return None

    def get_mappings(self) -> Dict[str, Any]:
        """Get all current mappings."""
        return self.mappings.copy()
