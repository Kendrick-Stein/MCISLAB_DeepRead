#!/usr/bin/env python3
"""
Validate YAML frontmatter in markdown files.
Checks all .md files in Papers/ directory for valid YAML syntax.
"""

import sys
import yaml
from pathlib import Path


def validate_frontmatter(filepath):
    """Validate YAML frontmatter in a markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            return True, None

        parts = content.split('---', 2)
        if len(parts) < 3:
            return False, "Invalid frontmatter format"

        yaml.safe_load(parts[1])
        return True, None

    except yaml.YAMLError as e:
        error_msg = str(e).split('\n')[0]
        return False, error_msg
    except Exception as e:
        return False, str(e)


def main():
    """Validate all markdown files in Papers/ directory."""
    papers_dir = Path(__file__).parent.parent / 'Papers'

    if not papers_dir.exists():
        print(f"Error: {papers_dir} not found")
        sys.exit(1)

    md_files = list(papers_dir.glob('*.md'))
    if not md_files:
        print("No markdown files found")
        sys.exit(0)

    errors = []
    for filepath in sorted(md_files):
        valid, error = validate_frontmatter(filepath)
        if not valid:
            errors.append((filepath.name, error))

    if errors:
        print(f"❌ Found {len(errors)} file(s) with invalid YAML:\n")
        for filename, error in errors:
            print(f"  {filename}: {error}")
        sys.exit(1)
    else:
        print(f"✅ All {len(md_files)} markdown files have valid YAML frontmatter")
        sys.exit(0)


if __name__ == '__main__':
    main()
