"""Tests for CSS parser module."""


from css_to_rust.parser import CssKeyframe, CssParser, CssRule


class TestCssParser:
    """Test CssParser class."""

    def setup_method(self):
        """Set up test instance."""
        self.parser = CssParser()

    def test_parse_simple_rule(self):
        """Test parsing a simple CSS rule."""
        css = """
        .button {
            background-color: blue;
            color: white;
            padding: 10px;
        }
        """
        rules = self.parser.parse(css)

        assert len(rules) == 1
        assert rules[0].selector == ".button"
        assert len(rules[0].properties) == 3

        # Check properties
        assert rules[0].properties["background-color"] == "blue"
        assert rules[0].properties["color"] == "white"
        assert rules[0].properties["padding"] == "10px"

    def test_parse_multiple_rules(self):
        """Test parsing multiple CSS rules."""
        css = """
        .header {
            font-size: 24px;
        }

        .footer {
            font-size: 14px;
        }
        """
        rules = self.parser.parse(css)

        assert len(rules) == 2
        assert rules[0].selector == ".header"
        assert rules[1].selector == ".footer"

    def test_parse_complex_selectors(self):
        """Test parsing complex selectors."""
        css = """
        .container > .item {
            margin: 10px;
        }

        #main .active {
            color: red;
        }

        div.card[data-active="true"] {
            border: 1px solid black;
        }
        """
        rules = self.parser.parse(css)

        assert len(rules) >= 3
        # Selectors might be normalized by cssutils
        selectors = [rule.selector for rule in rules]
        assert any(".container" in s for s in selectors)
        assert any("#main" in s for s in selectors)
        assert any("div.card" in s or "card" in s for s in selectors)

    def test_parse_media_query(self):
        """Test parsing media queries."""
        css = """
        @media (max-width: 768px) {
            .responsive {
                width: 100%;
            }
        }
        """
        rules = self.parser.parse(css)

        assert len(rules) == 1
        assert rules[0].selector == ".responsive"
        assert rules[0].media_query == "(max-width: 768px)"
        assert rules[0].properties["width"] == "100%"

    def test_parse_shorthand_properties(self):
        """Test parsing shorthand properties."""
        css = """
        .box {
            margin: 10px 20px 30px 40px;
            border: 1px solid black;
            font: bold 16px/1.5 Arial, sans-serif;
        }
        """
        rules = self.parser.parse(css)

        assert len(rules) == 1
        # Shorthand properties might be expanded by cssutils
        assert "margin" in rules[0].properties or "margin-top" in rules[0].properties
        assert "border" in rules[0].properties or "border-width" in rules[0].properties
        assert "font" in rules[0].properties or "font-size" in rules[0].properties

    def test_parse_pseudo_selectors(self):
        """Test parsing pseudo-selectors."""
        css = """
        .button:hover {
            background-color: darkblue;
        }

        .input:focus {
            outline: none;
        }
        """
        rules = self.parser.parse(css)

        assert len(rules) == 2
        # Check if pseudo-selectors are handled
        for rule in rules:
            assert rule.selector in [".button", ".input"] or rule.pseudo_selector in [
                "hover",
                "focus",
            ]

    def test_parse_comments(self):
        """Test parsing with comments."""
        css = """
        /* Header styles */
        .header {
            /* Primary color */
            color: #007bff;
            background: white; /* Background color */
        }
        """
        rules = self.parser.parse(css)

        assert len(rules) == 1
        assert len(rules[0].properties) >= 2
        assert "color" in rules[0].properties
        assert "background" in rules[0].properties

    def test_parse_empty_rules(self):
        """Test parsing empty rules."""
        css = """
        .empty {
        }

        .with-content {
            display: block;
        }
        """
        rules = self.parser.parse(css)

        # Empty rules might be filtered out
        assert len(rules) >= 1
        # At least the non-empty rule should be present
        non_empty = [r for r in rules if r.properties]
        assert len(non_empty) >= 1
        assert any(r.properties.get("display") == "block" for r in rules)

    def test_parse_vendor_prefixes(self):
        """Test parsing vendor prefixes."""
        css = """
        .prefixed {
            -webkit-transform: rotate(45deg);
            -moz-transform: rotate(45deg);
            transform: rotate(45deg);
        }
        """
        rules = self.parser.parse(css)

        assert len(rules) == 1
        props = rules[0].properties
        # Vendor prefixes should be preserved
        assert "-webkit-transform" in props or "transform" in props
        assert any("rotate(45deg)" in v for v in props.values())

    def test_parse_keyframes(self):
        """Test parsing keyframes."""
        css = """
        @keyframes slideIn {
            0% {
                transform: translateX(-100%);
            }
            100% {
                transform: translateX(0);
            }
        }
        """
        self.parser.parse(css)

        # Check keyframes were parsed
        assert len(self.parser.keyframes) == 1
        keyframe = self.parser.keyframes[0]
        assert keyframe.name == "slideIn"
        assert "0%" in keyframe.keyframes
        assert "100%" in keyframe.keyframes

    def test_group_rules_by_component(self):
        """Test grouping rules by component."""
        css = """
        .btn-primary {
            background: blue;
        }
        .btn-secondary {
            background: gray;
        }
        .card-header {
            font-weight: bold;
        }
        """
        rules = self.parser.parse(css)
        groups = self.parser.group_rules_by_component(rules)

        assert "button" in groups
        assert "card" in groups
        assert len(groups["button"]) == 2
        assert len(groups["card"]) == 1

    def test_get_function_name_from_selector(self):
        """Test generating Rust function names from selectors."""
        parser = self.parser

        # Basic selectors
        assert parser.get_function_name_from_selector(".my-class") == "my_class"
        assert parser.get_function_name_from_selector("#my-id") == "my_id"
        assert parser.get_function_name_from_selector("div") == "div"

        # With pseudo-selectors
        assert parser.get_function_name_from_selector(".btn", "hover") == "btn_hover"
        assert (
            parser.get_function_name_from_selector(".input", "focus") == "input_focus"
        )

        # Complex selectors
        assert (
            parser.get_function_name_from_selector(".parent > .child") == "parent_child"
        )
        assert (
            parser.get_function_name_from_selector("div.card[data-active]")
            == "div_card_data_active"
        )

        # Starting with numbers
        assert parser.get_function_name_from_selector("123-class") == "style_123_class"

    def test_extract_variants(self):
        """Test extracting style variants."""
        css = """
        .btn-primary {
            background: blue;
        }
        .btn-secondary {
            background: gray;
        }
        .btn-large {
            font-size: 18px;
        }
        """
        rules = self.parser.parse(css)
        variants = self.parser.extract_variants(rules)

        assert "btn_primary" in variants
        assert "btn_secondary" in variants
        assert "btn_large" in variants

    def test_fallback_regex_parsing(self):
        """Test fallback regex parsing when cssutils fails."""
        # Create invalid CSS that might fail cssutils
        css = """
        .valid { color: red; }
        @invalid-rule { something: wrong; }
        .another { color: blue; }
        """

        # Force regex parsing by using invalid CSS
        parser = CssParser()
        rules = parser._parse_with_regex(css)

        # Should still parse valid rules
        assert len(rules) >= 2
        assert any(r.selector == ".valid" for r in rules)
        assert any(r.selector == ".another" for r in rules)


class TestCssRule:
    """Test CssRule class."""

    def test_rule_creation(self):
        """Test creating a CSS rule."""
        rule = CssRule(
            selector=".test-class",
            properties={"color": "red", "margin": "10px"},
            media_query=None,
            pseudo_selector=None,
            raw_css=".test-class { color: red; margin: 10px; }",
        )

        assert rule.selector == ".test-class"
        assert rule.properties["color"] == "red"
        assert rule.properties["margin"] == "10px"
        assert rule.media_query is None
        assert rule.pseudo_selector is None

    def test_rule_with_media_query(self):
        """Test rule with media query."""
        rule = CssRule(
            selector=".responsive",
            properties={"width": "100%"},
            media_query="(max-width: 768px)",
            pseudo_selector=None,
            raw_css="",
        )

        assert rule.media_query == "(max-width: 768px)"
        assert rule.properties["width"] == "100%"

    def test_rule_with_pseudo_selector(self):
        """Test rule with pseudo-selector."""
        rule = CssRule(
            selector=".button",
            properties={"background": "blue"},
            media_query=None,
            pseudo_selector="hover",
            raw_css="",
        )

        assert rule.pseudo_selector == "hover"
        assert rule.selector == ".button"


class TestCssKeyframe:
    """Test CssKeyframe class."""

    def test_keyframe_creation(self):
        """Test creating a CSS keyframe."""
        keyframe = CssKeyframe(
            name="slideIn",
            keyframes={
                "0%": {"transform": "translateX(-100%)"},
                "100%": {"transform": "translateX(0)"},
            },
        )

        assert keyframe.name == "slideIn"
        assert len(keyframe.keyframes) == 2
        assert keyframe.keyframes["0%"]["transform"] == "translateX(-100%)"
        assert keyframe.keyframes["100%"]["transform"] == "translateX(0)"
