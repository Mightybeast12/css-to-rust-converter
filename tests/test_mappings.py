"""Tests for CSS to Rust value mappings."""


from css_to_rust.mappings import ValueMappings


class TestValueMappings:
    """Test ValueMappings class."""

    def setup_method(self):
        """Set up test instance."""
        self.mappings = ValueMappings()

    def test_default_mappings_loaded(self):
        """Test that default mappings are loaded correctly."""
        mappings = self.mappings.get_mappings()
        assert "colors" in mappings
        assert "spacing" in mappings
        assert "border_radius" in mappings
        assert "font_sizes" in mappings
        assert "font_weights" in mappings

    def test_color_mapping(self):
        """Test color value mappings."""
        # Test hex color mapping
        assert self.mappings.map_value("color", "#007bf") == "var(--color-primary)"
        assert (
            self.mappings.map_value("background-color", "#ffffff")
            == "var(--color-background)"
        )

        # Test color keywords
        assert self.mappings.map_value("color", "white") == "var(--color-background)"
        assert self.mappings.map_value("color", "black") == "var(--color-text-primary)"
        assert self.mappings.map_value("color", "transparent") == "transparent"

    def test_spacing_mapping(self):
        """Test spacing value mappings."""
        # Pixel values
        assert self.mappings.map_value("padding", "8px") == "var(--spacing-sm)"
        assert self.mappings.map_value("margin", "16px") == "var(--spacing-md)"
        assert self.mappings.map_value("gap", "32px") == "var(--spacing-xl)"

        # REM values
        assert self.mappings.map_value("padding", "0.5rem") == "var(--spacing-sm)"
        assert self.mappings.map_value("margin", "1rem") == "var(--spacing-md)"

    def test_border_radius_mapping(self):
        """Test border radius mappings."""
        assert (
            self.mappings.map_value("border-radius", "4px") == "var(--border-radius-sm)"
        )
        assert (
            self.mappings.map_value("border-radius", "8px") == "var(--border-radius-md)"
        )
        assert self.mappings.map_value("border-radius", "50%") == "50%"
        assert (
            self.mappings.map_value("border-radius", "9999px")
            == "var(--border-radius-full)"
        )

    def test_font_size_mapping(self):
        """Test font size mappings."""
        assert self.mappings.map_value("font-size", "14px") == "var(--font-size-sm)"
        assert self.mappings.map_value("font-size", "16px") == "var(--font-size-md)"
        assert self.mappings.map_value("font-size", "1rem") == "var(--font-size-md)"
        assert self.mappings.map_value("font-size", "1.5rem") == "var(--font-size-xxl)"

    def test_font_weight_mapping(self):
        """Test font weight mappings."""
        assert (
            self.mappings.map_value("font-weight", "400") == "var(--font-weight-normal)"
        )
        assert (
            self.mappings.map_value("font-weight", "700") == "var(--font-weight-bold)"
        )
        assert (
            self.mappings.map_value("font-weight", "normal")
            == "var(--font-weight-normal)"
        )
        assert (
            self.mappings.map_value("font-weight", "bold") == "var(--font-weight-bold)"
        )

    def test_unmapped_values(self):
        """Test that unmapped values are returned as-is."""
        assert self.mappings.map_value("color", "#123456") == "#123456"
        assert self.mappings.map_value("padding", "25px") == "25px"
        assert self.mappings.map_value("font-size", "13px") == "13px"

    def test_property_category_detection(self):
        """Test _get_category_for_property method."""
        # Color properties
        assert self.mappings._get_category_for_property("color") == "colors"
        assert self.mappings._get_category_for_property("background-color") == "colors"
        assert self.mappings._get_category_for_property("border-color") == "colors"

        # Spacing properties
        assert self.mappings._get_category_for_property("padding") == "spacing"
        assert self.mappings._get_category_for_property("margin-top") == "spacing"
        assert self.mappings._get_category_for_property("gap") == "spacing"

        # Font properties
        assert self.mappings._get_category_for_property("font-size") == "font_sizes"
        assert self.mappings._get_category_for_property("font-weight") == "font_weights"

        # Border radius
        assert (
            self.mappings._get_category_for_property("border-radius") == "border_radius"
        )

        # Unknown property
        assert self.mappings._get_category_for_property("unknown-property") is None
