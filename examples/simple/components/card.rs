//! Card component styles

use stylist::Style;

pub fn card() -> Style {
    Style::new(
        r#"{
            background: var(--color-background);
            border: 1px solid #dee2e6;
            border-radius: var(--border-radius-md);
            padding: var(--spacing-md);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        &: hover {;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transform: translateY(-1px);
        }
         {
            padding: var(--spacing-md);
        }

        @media (max-width: 768px) {
             {
                padding: var(--spacing-md);
            }
        }
    "#,
    )
    .expect("Failed to create card styles")
}
