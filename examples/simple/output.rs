//! Generated CSS styles

use stylist::Style;

pub fn button() -> Style {
    Style::new(
        r#"{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 8px 16px;
            border-radius: var(--border-radius-sm);
            border: none;
            cursor: pointer;
            font-size: var(--font-size-sm);
            font-weight: var(--font-weight-medium);
            transition: var(--transition-fast);
            background: var(--color-primary);
            color: var(--color-background);
        }
        &: hover {;
            background: var(--color-primary-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        &: focus {;
            outline: 2px solid #007bff;
            outline-offset: var(--spacing-xs);
        }

        @media (max-width: 768px) {
             {
                width: 100%;
                padding: 12px 16px;
            }
        }
    "#,
    )
    .expect("Failed to create button styles")
}

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

pub fn button_secondary() -> Style {
    Style::new(
        r#"{
            background: var(--color-text-secondary);
            color: var(--color-background);
        }
        &: hover {;
            background: var(--color-secondary-hover);
        }
    "#,
    )
    .expect("Failed to create button_secondary styles")
}

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

pub fn hidden() -> Style {
    Style::new(
        r#"{
            display: none;
        }
    "#,
    )
    .expect("Failed to create hidden styles")
}

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
