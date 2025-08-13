//! @Media component styles

use stylist::Style;

pub fn media_max_width() -> Style {
    Style::new(
        r#"&: 768px) {;
            .button {
        width: 100%;
            padding: 12px 16px;
        }
    "#,
    )
    .expect("Failed to create media_max_width styles")
}
