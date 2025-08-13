//! Hidden component styles

use stylist::Style;

pub fn hidden() -> Style {
    Style::new(
        r#"{
            display: none;
        }
    "#,
    )
    .expect("Failed to create hidden styles")
}
