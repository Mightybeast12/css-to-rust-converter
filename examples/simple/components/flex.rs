//! Flex component styles

use stylist::Style;

pub fn flex_center() -> Style {
    Style::new(
        r#"{
            display: flex;
            align-items: center;
            justify-content: center;
        }
    "#,
    )
    .expect("Failed to create flex_center styles")
}
