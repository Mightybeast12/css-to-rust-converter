#!/usr/bin/env python3
"""
Release script for css-to-rust-converter - reads version from setup.py/pyproject.toml
Usage: ./release.py [--dry-run|--help|--test-pypi]
"""

import argparse
import subprocess
import sys
import os
import re
from pathlib import Path
from datetime import datetime

# ANSI color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color

def print_error(msg):
    print(f"{RED}❌ Error: {msg}{NC}", file=sys.stderr)

def print_success(msg):
    print(f"{GREEN}✅ {msg}{NC}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{NC}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{NC}")

def print_step(msg):
    print(f"{CYAN}🔄 {msg}{NC}")

def run_command(cmd, check=True, capture_output=False):
    """Run a shell command."""
    print_info(f"Running: {cmd}")
    if capture_output:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print_error(f"Command failed: {cmd}")
            print(result.stderr)
            sys.exit(1)
        return result.stdout.strip()
    else:
        result = subprocess.run(cmd, shell=True)
        if check and result.returncode != 0:
            print_error(f"Command failed: {cmd}")
            sys.exit(1)
        return None

def get_current_version():
    """Get the current version from setup.py or pyproject.toml."""
    # Try setup.py first
    if Path("setup.py").exists():
        try:
            result = run_command("python setup.py --version", capture_output=True)
            if result:
                return result
        except:
            pass

        # Parse setup.py manually
        with open("setup.py", "r") as f:
            content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)

    # Try pyproject.toml
    if Path("pyproject.toml").exists():
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                print_warning("tomli not installed, trying regex parsing")
                with open("pyproject.toml", "r") as f:
                    content = f.read()
                    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)
                return None

        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "")

    return None

def update_changelog(version, dry_run=False):
    """Update CHANGELOG.md with the current date for the version."""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print_warning("CHANGELOG.md not found, skipping changelog update")
        return

    current_date = datetime.now().strftime("%Y-%m-%d")

    if dry_run:
        print_info(f"Would update CHANGELOG.md for version {version}")
        return

    with open(changelog_path, "r") as f:
        content = f.read()

    # Replace [Unreleased] with [Unreleased] and new version section
    new_content = content.replace(
        "## [Unreleased]",
        f"## [Unreleased]\n\n## [{version}] - {current_date}"
    )

    with open(changelog_path, "w") as f:
        f.write(new_content)

    print_success(f"Updated CHANGELOG.md for version {version}")

def run_tests(dry_run=False):
    """Run the test suite."""
    print_step("Running test suite...")

    if dry_run:
        print_info("Would run: ./test-local.py")
        return

    if Path("test-local.py").exists():
        run_command("python test-local.py")
    else:
        # Fallback to pytest
        run_command("pytest -v")

    print_success("All tests passed")

def check_git_status(dry_run=False):
    """Check git repository status."""
    print_step("Checking git status...")

    # Check if on main branch
    current_branch = run_command("git branch --show-current", capture_output=True)
    if current_branch != "main":
        print_error(f"Not on main branch (currently on: {current_branch})")
        print_info("Fix: git checkout main")
        sys.exit(1)

    # Check for uncommitted changes
    status = run_command("git status --porcelain", capture_output=True)
    if status and not dry_run:
        print_error("Uncommitted changes detected")
        print_info("Fix: Commit or stash your changes")
        sys.exit(1)

    if not dry_run:
        # Fetch latest
        run_command("git fetch origin main --quiet")

        # Check if up to date
        local_commit = run_command("git rev-parse HEAD", capture_output=True)
        remote_commit = run_command("git rev-parse origin/main", capture_output=True)

        if local_commit != remote_commit:
            # Check if need to pull
            merge_base = run_command(f"git merge-base {local_commit} {remote_commit}", capture_output=True)
            if merge_base == local_commit:
                print_error("Local branch is behind origin/main")
                print_info("Fix: git pull origin main")
                sys.exit(1)

    print_success("Git status OK")

def create_tag_and_push(version, dry_run=False, test_pypi=False):
    """Create git tag and push to remote."""
    tag = f"v{version}"

    # Handle existing tags
    existing_tags = run_command("git tag -l", capture_output=True).split('\n')
    if tag in existing_tags:
        print_warning(f"Tag {tag} already exists locally")
        if not dry_run:
            print_step(f"Removing existing tag {tag}")
            run_command(f"git tag -d {tag}")

    if dry_run:
        print_info(f"Would create tag: {tag}")
        print_info("Would push to origin/main")
        return

    print_step("Committing version changes...")
    run_command("git add setup.py pyproject.toml CHANGELOG.md")

    # Check if there are changes to commit
    if run_command("git diff --cached --quiet", check=False).returncode != 0:
        run_command(f'git commit -m "chore: release v{version}"')
    else:
        print_warning("No changes to commit")

    print_step(f"Creating git tag {tag}...")
    run_command(f'git tag -a {tag} -m "Release {tag}"')

    print_step("Pushing to remote...")
    run_command("git push origin main")
    run_command(f"git push origin {tag}")

    print_success(f"Release {tag} completed successfully!")
    print()

    if test_pypi:
        print_info("GitHub Actions will now:")
        print_info("- Run CI checks")
        print_info("- Publish to TestPyPI")
        print_info("- Create GitHub release (pre-release)")
    else:
        print_info("GitHub Actions will now:")
        print_info("- Run CI checks")
        print_info("- Publish to PyPI")
        print_info("- Create GitHub release")

    print()
    repo_url = run_command("git config --get remote.origin.url", capture_output=True)
    if "github.com" in repo_url:
        repo_path = re.search(r'github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$', repo_url)
        if repo_path:
            print_info(f"View release: https://github.com/{repo_path.group(1)}/releases/tag/{tag}")

def main():
    parser = argparse.ArgumentParser(description="Release script for Python packages")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    parser.add_argument("--test-pypi", action="store_true", help="Release to TestPyPI (creates rc tag)")
    args = parser.parse_args()

    print_step(f"Preparing release for css-to-rust-converter")

    # Get version
    version = get_current_version()
    if not version:
        print_error("Could not determine version from setup.py or pyproject.toml")
        sys.exit(1)

    # Add rc suffix for test releases
    if args.test_pypi and "rc" not in version:
        print_error("For TestPyPI releases, version should contain 'rc' (e.g., 1.0.0rc1)")
        sys.exit(1)

    print_info(f"Version: {version}")

    # Run checks
    check_git_status(args.dry_run)

    # Update changelog
    update_changelog(version, args.dry_run)

    # Run tests
    run_tests(args.dry_run)

    # Create tag and push
    create_tag_and_push(version, args.dry_run, args.test_pypi)

if __name__ == "__main__":
    main()
