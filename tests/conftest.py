"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Shared fixtures can be added here
import pytest


@pytest.fixture
def sample_css():
    """Provide sample CSS for testing."""
    return """
    .button {
        background-color: #007bff;
        color: white;
        padding: 10px 20px;
        border-radius: 4px;
    }

    .button:hover {
        background-color: #0056b3;
    }

    @media (max-width: 768px) {
        .button {
            width: 100%;
        }
    }
    """


@pytest.fixture
def sample_css_with_variables():
    """Provide CSS with variables for testing."""
    return """
    :root {
        --primary-color: #007bff;
        --secondary-color: #6c757d;
        --spacing-sm: 8px;
        --spacing-md: 16px;
    }

    .card {
        background: var(--secondary-color);
        padding: var(--spacing-md);
        color: var(--primary-color);
    }
    """
