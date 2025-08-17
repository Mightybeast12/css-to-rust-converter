"""Tests for CSS to Rust utility functions."""

import pytest
from css_to_rust.utils import (
    normalize_selector,
    extract_class_name,
    is_valid_rust_identifier,
    sanitize_rust_identifier,
    format_css_property,
    detect_css_framework,
    estimate_conversion_complexity,
    group_related_selectors,
    optimize_css_content,
    validate_css_syntax,
    extract_color_palette,
    calculate_specificity,
)


class TestNormalizeSelector:
    """Test normalize_selector function."""

    def test_extra_whitespace(self):
        """Test removing extra whitespace."""
        assert normalize_selector("  .class   .child  ") == ".class .child"
        assert normalize_selector(".class\n.child") == ".class .child"
        assert normalize_selector(".class\t.child") == ".class .child"

    def test_pseudo_selectors(self):
        """Test normalizing pseudo-selectors."""
        assert normalize_selector(".class : hover") == ".class:hover"
        assert normalize_selector(".class :: before") == ".class::before"
        assert normalize_selector(".class :not(.other)") == ".class:not(.other)"


class TestExtractClassName:
    """Test extract_class_name function."""

    def test_class_selectors(self):
        """Test extracting class names."""
        assert extract_class_name(".my-class") == "my-class"
        assert extract_class_name(".my-class:hover") == "my-class"
        assert extract_class_name(".parent .child") == "parent"

    def test_id_selectors(self):
        """Test extracting ID names."""
        assert extract_class_name("#my-id") == "my-id"
        assert extract_class_name("#my-id:focus") == "my-id"

    def test_element_selectors(self):
        """Test extracting element names."""
        assert extract_class_name("div") == "div"
        assert extract_class_name("button:hover") == "button"

    def test_complex_selectors(self):
        """Test complex selectors."""
        assert extract_class_name(".parent > .child") == "parent"
        assert extract_class_name("div.class") is None


class TestRustIdentifier:
    """Test Rust identifier functions."""

    def test_is_valid_rust_identifier(self):
        """Test is_valid_rust_identifier function."""
        # Valid identifiers
        assert is_valid_rust_identifier("my_class") is True
        assert is_valid_rust_identifier("MyClass") is True
        assert is_valid_rust_identifier("_private") is True
        assert is_valid_rust_identifier("class123") is True

        # Invalid identifiers
        assert is_valid_rust_identifier("my-class") is False
        assert is_valid_rust_identifier("123class") is False
        assert is_valid_rust_identifier("my.class") is False
        assert is_valid_rust_identifier("my class") is False
        assert is_valid_rust_identifier("") is False

    def test_sanitize_rust_identifier(self):
        """Test sanitize_rust_identifier function."""
        # Basic sanitization
        assert sanitize_rust_identifier("my-class") == "my_class"
        assert sanitize_rust_identifier("my.class") == "my_class"
        assert sanitize_rust_identifier("my class") == "my_class"
        assert sanitize_rust_identifier("my/class") == "my_class"

        # Special cases
        assert sanitize_rust_identifier("") == "style"
        assert sanitize_rust_identifier("123") == "style_123"
        assert sanitize_rust_identifier("@media") == "media"

        # Reserved keywords
        assert sanitize_rust_identifier("impl") == "impl_style"
        assert sanitize_rust_identifier("struct") == "struct_style"
        assert sanitize_rust_identifier("type") == "type_style"


class TestFormatCssProperty:
    """Test format_css_property function."""

    def test_basic_formatting(self):
        """Test basic property formatting."""
        assert format_css_property("color", "red") == "color: red;"
        assert format_css_property("margin", "10px") == "margin: 10px;"
        assert format_css_property("  padding  ", "  20px  ") == "padding: 20px;"

    def test_remove_trailing_semicolon(self):
        """Test removing trailing semicolons from values."""
        assert format_css_property("color", "red;") == "color: red;"
        assert format_css_property("margin", "10px;;") == "margin: 10px;"


class TestDetectCssFramework:
    """Test detect_css_framework function."""

    def test_bootstrap_detection(self):
        """Test Bootstrap detection."""
        assert detect_css_framework(".btn-primary { }") == "bootstrap"
        assert detect_css_framework(".card-header { }") == "bootstrap"
        assert detect_css_framework("/* Bootstrap v5 */") == "bootstrap"

    def test_tailwind_detection(self):
        """Test Tailwind detection."""
        assert detect_css_framework("@tailwind base;") == "tailwind"
        assert detect_css_framework(".prose-lg { }") == "tailwind"

    def test_bulma_detection(self):
        """Test Bulma detection."""
        assert detect_css_framework(".is-primary { }") == "bulma"
        assert detect_css_framework(".has-text-centered { }") == "bulma"

    def test_no_framework(self):
        """Test when no framework is detected."""
        assert detect_css_framework(".my-custom-class { }") is None


class TestEstimateConversionComplexity:
    """Test estimate_conversion_complexity function."""

    def test_simple_css(self):
        """Test complexity estimation for simple CSS."""
        css = ".class { color: red; }"
        complexity = estimate_conversion_complexity(css)

        assert complexity["total_lines"] == 1
        assert complexity["rules_count"] == 1
        assert complexity["media_queries"] == 0
        assert complexity["difficulty"] == "easy"

    def test_complex_css(self):
        """Test complexity estimation for complex CSS."""
        css = """
        @media (max-width: 768px) {
            .responsive { width: 100%; }
        }
        .class:hover::before {
            content: "";
            width: calc(100% - 20px);
        }
        """
        complexity = estimate_conversion_complexity(css)

        assert complexity["media_queries"] > 0
        assert complexity["pseudo_selectors"] > 0
        assert complexity["calc_functions"] > 0


class TestGroupRelatedSelectors:
    """Test group_related_selectors function."""

    def test_basic_grouping(self):
        """Test basic selector grouping."""
        selectors = [".button", ".button-primary", ".button-secondary", ".card", ".card-header"]
        groups = group_related_selectors(selectors)

        assert "button" in groups
        assert "card" in groups
        assert len(groups["button"]) == 3
        assert len(groups["card"]) == 2

    def test_no_base_name(self):
        """Test selectors without extractable base names."""
        selectors = ["div > span", "* + *"]
        groups = group_related_selectors(selectors)

        assert len(groups) == 0


class TestOptimizeCssContent:
    """Test optimize_css_content function."""

    def test_remove_comments(self):
        """Test comment removal."""
        css = "/* Comment */ .class { color: red; /* inline */ }"
        optimized = optimize_css_content(css)

        assert "Comment" not in optimized
        assert "inline" not in optimized
        assert ".class" in optimized

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        css = """
        .class    {
            color:    red;
        }
        """
        optimized = optimize_css_content(css)

        assert "    " not in optimized  # No excessive spaces


class TestValidateCssSyntax:
    """Test validate_css_syntax function."""

    def test_valid_css(self):
        """Test valid CSS syntax."""
        css = ".class { color: red; }"
        errors = validate_css_syntax(css)

        assert len(errors) == 0

    def test_unbalanced_braces(self):
        """Test detecting unbalanced braces."""
        css = ".class { color: red; } }"
        errors = validate_css_syntax(css)

        assert len(errors) > 0
        assert "Unbalanced braces" in errors[0]

    def test_missing_semicolon(self):
        """Test detecting missing semicolons."""
        css = ".class { color: red }"
        errors = validate_css_syntax(css)

        assert len(errors) > 0
        assert "Missing semicolon" in errors[0]

    def test_empty_selectors(self):
        """Test detecting empty selectors."""
        css = ".class { } .other { color: red; }"
        errors = validate_css_syntax(css)

        assert len(errors) > 0
        assert "empty rule" in errors[0]


class TestExtractColorPalette:
    """Test extract_color_palette function."""

    def test_hex_colors(self):
        """Test extracting hex colors."""
        css = ".class { color: #fff; background: #123456; }"
        colors = extract_color_palette(css)

        assert "#fff" in colors["hex"]
        assert "#123456" in colors["hex"]

    def test_rgb_colors(self):
        """Test extracting RGB colors."""
        css = ".class { color: rgb(255, 0, 0); background: rgba(0, 0, 0, 0.5); }"
        colors = extract_color_palette(css)

        assert "rgb(255, 0, 0)" in colors["rgb"]
        assert "rgba(0, 0, 0, 0.5)" in colors["rgba"]

    def test_named_colors(self):
        """Test extracting named colors."""
        css = ".class { color: red; background: blue; border: 1px solid black; }"
        colors = extract_color_palette(css)

        assert "red" in colors["named"]
        assert "blue" in colors["named"]
        assert "black" in colors["named"]


class TestCalculateSpecificity:
    """Test calculate_specificity function."""

    def test_element_specificity(self):
        """Test element selector specificity."""
        assert calculate_specificity("div") == 1
        assert calculate_specificity("div span") == 2

    def test_class_specificity(self):
        """Test class selector specificity."""
        assert calculate_specificity(".class") == 10
        assert calculate_specificity(".class1.class2") == 20

    def test_id_specificity(self):
        """Test ID selector specificity."""
        assert calculate_specificity("#id") == 100
        assert calculate_specificity("#id1#id2") == 200

    def test_combined_specificity(self):
        """Test combined selector specificity."""
        assert calculate_specificity("div.class#id") == 111  # 1 + 10 + 100
        assert calculate_specificity(".class:hover") == 20  # 10 + 10 (pseudo-class)
        assert calculate_specificity("input[type='text']") == 11  # 1 + 10 (attribute)
