# CSS-to-Rust Converter

A comprehensive tool for converting CSS styles to Rust `stylist` format for Yew applications.

## Features

- 🎯 **Smart CSS Parsing** - Handles complex CSS with media queries, pseudo-selectors, and keyframes
- 🔄 **Value Mapping** - Automatically maps CSS values to theme variables
- 📦 **Component Grouping** - Groups related styles into Rust modules
- 🎨 **Variant Detection** - Extracts style variants (e.g., btn-primary, btn-secondary)
- 🛠️ **CLI Interface** - Rich command-line interface with progress bars and colored output
- ⚙️ **Configurable** - Custom mappings via JSON configuration
- 📊 **Analysis Tools** - CSS analysis and validation utilities

## Installation

```bash
cd css-to-rust-converter
pip install -r requirements.txt
pip install -e .
# or
pipx install .
```

## Quick Start

### Convert a Single File

```bash
python -m css_to_rust convert input.css -o output.rs
```

### Convert with Component Grouping

```bash
python -m css_to_rust convert input.css -o ./styles/ --component
```

### Analyze CSS Before Converting

```bash
python -m css_to_rust analyze input.css
```

### Preview Conversion

```bash
python -m css_to_rust preview ".button { padding: 8px 16px; background: #007bff; }"
```

## Examples

### Input CSS
```css
.button {
    display: inline-flex;
    padding: 8px 16px;
    border-radius: 4px;
    background: #007bff;
    color: white;
}

.button:hover {
    background: #0056b3;
    transform: translateY(-2px);
}

.button-secondary {
    background: #6c757d;
}
```

### Output Rust
```rust
//! Button component styles

use stylist::Style;

pub fn button() -> Style {
    Style::new(
        r#"
        display: inline-flex;
        padding: var(--spacing-sm) var(--spacing-md);
        border-radius: var(--border-radius-sm);
        background: var(--color-primary);
        color: white;

        &:hover {
            background: var(--color-primary-hover);
            transform: translateY(-2px);
        }
    "#,
    )
    .expect("Failed to create button styles")
}

pub fn button_secondary() -> Style {
    Style::new(
        r#"
        background: var(--color-secondary);
    "#,
    )
    .expect("Failed to create button_secondary styles")
}
```

## Command Reference

### Convert Command

```bash
python -m css_to_rust convert <input> [OPTIONS]
```

**Options:**
- `-o, --output PATH` - Output file or directory
- `-c, --config PATH` - Custom configuration file
- `--component` - Group by component and create module structure
- `--no-variants` - Disable variant extraction
- `--utilities` - Include utility functions
- `--analyze` - Show analysis before conversion

### Analyze Command

```bash
python -m css_to_rust analyze <css_file>
```

Shows detailed statistics about your CSS:
- Rule counts and complexity
- Component detection
- Value mapping coverage
- Framework detection

### Validate Command

```bash
python -m css_to_rust validate <css_file>
```

Checks CSS for conversion compatibility and potential issues.

### Preview Command

```bash
python -m css_to_rust preview <css_string> [OPTIONS]
```

**Options:**
- `--component` - Group by component
- `--no-variants` - Disable variant extraction

## Configuration

### Custom Value Mappings

Create a JSON file with custom mappings:

```json
{
    "colors": {
        "#007bff": "var(--color-primary)",
        "#6c757d": "var(--color-secondary)"
    },
    "spacing": {
        "8px": "var(--spacing-sm)",
        "16px": "var(--spacing-md)"
    }
}
```

Use with `-c config.json` flag.

### Default Mappings

The tool includes comprehensive default mappings for:
- ✅ Colors (hex, rgb, named)
- ✅ Spacing (px, rem)
- ✅ Border radius
- ✅ Font sizes and weights
- ✅ Shadows
- ✅ Transitions
- ✅ Breakpoints

## Advanced Usage

### Component Structure Output

When using `--component`, the tool creates organized modules:

```
styles/
├── mod.rs
├── button.rs
├── card.rs
└── navbar.rs
```

### Utility Functions

Include common utility functions with `--utilities`:

```rust
pub fn flex_center() -> Style { /* ... */ }
pub fn hidden() -> Style { /* ... */ }
pub fn text_center() -> Style { /* ... */ }
```

### Framework Detection

The tool automatically detects CSS frameworks:
- Bootstrap
- Tailwind CSS
- Bulma
- Foundation

And applies appropriate conversion strategies.

## Integration with Yew

Use the generated styles in your Yew components:

```rust
use crate::styles::components::button::*;

#[function_component(MyButton)]
pub fn my_button() -> Html {
    html! {
        <button class={button()}>
            {"Click me"}
        </button>
    }
}
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Project Structure

```
css-to-rust-converter/
├── css_to_rust/           # Main package
│   ├── __init__.py
│   ├── __main__.py        # CLI entry point
│   ├── converter.py       # Main converter logic
│   ├── parser.py          # CSS parsing
│   ├── generator.py       # Rust code generation
│   ├── mappings.py        # Value mappings
│   └── utils.py           # Utility functions
├── config/                # Configuration files
├── examples/              # Example conversions
├── tests/                 # Test suite
└── templates/             # Code templates
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Changelog

### v1.0.0
- Initial release
- Full CSS parsing support
- Component grouping
- Value mapping system
- CLI interface
- Analysis tools
