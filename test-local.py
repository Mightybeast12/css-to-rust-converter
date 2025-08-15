#!/usr/bin/env python3
"""Local test runner for comprehensive testing before commits."""

import subprocess
import sys
from pathlib import Path

# ANSI color codes
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{BLUE}📋 {description}...{NC}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"{RED}❌ {description} failed!{NC}")
        return False
    print(f"{GREEN}✅ {description} passed!{NC}")
    return True


def main():
    """Run all tests."""
    print(f"{BLUE}🧪 Running local tests...{NC}\n")

    all_passed = True

    # Format check with black
    if run_command("black --check .", "Checking formatting"):
        pass
    else:
        print(f"{YELLOW}💡 Fix with: black .{NC}")
        all_passed = False

    # Import sorting with isort
    if run_command("isort --check-only .", "Checking import sorting"):
        pass
    else:
        print(f"{YELLOW}💡 Fix with: isort .{NC}")
        all_passed = False

    # Linting with flake8
    if not run_command("flake8 .", "Running flake8"):
        all_passed = False

    # Type checking with mypy (optional)
    if Path("mypy.ini").exists() or Path("pyproject.toml").exists():
        if not run_command("mypy . --ignore-missing-imports", "Running mypy"):
            print(f"{YELLOW}⚠️  Type checking failed (non-blocking){NC}")

    # Security check with bandit
    if not run_command("bandit -r . -f screen", "Security check with bandit"):
        print(f"{YELLOW}⚠️  Security issues found (non-blocking){NC}")

    # Run tests
    if Path("tests").exists() or Path("test").exists():
        if not run_command(
            "pytest -v --cov=. --cov-report=term-missing", "Running tests"
        ):
            all_passed = False
    else:
        print(f"{YELLOW}⚠️  No tests directory found{NC}")

    # Documentation build
    if Path("docs").exists():
        if not run_command("cd docs && make html", "Building documentation"):
            print(f"{YELLOW}⚠️  Documentation build failed (non-blocking){NC}")

    print("\n" + "=" * 50)
    if all_passed:
        print(f"{GREEN}✅ All tests passed!{NC}")
        return 0
    else:
        print(f"{RED}❌ Some tests failed!{NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
