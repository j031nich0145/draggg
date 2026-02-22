#!/usr/bin/env python3
"""
Sync README.md content to Quarto .qmd files.
Preserves YAML frontmatter in .qmd files.
"""

import re
import sys
from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).parent.parent

# Section mappings: (qmd_file, list of section patterns to extract)
SECTION_MAPPINGS = {
    'index.qmd': [
        (r'^## Overview.*?(?=^## |\Z)', True),  # (pattern, include_header)
        (r'^## Features.*?(?=^## |\Z)', True),
        (r'^## Quick Install.*?(?=^## |\Z)', True),
        (r'^## How It Works.*?(?=^## |\Z)', True),
        (r'^## Supported Hardware.*?(?=^## |\Z)', True),
        (r'^## System Requirements.*?(?=^## |\Z)', True),
    ],
    'installation.qmd': [
        (r'^## Installation.*?(?=^## |\Z)', True),
        (r'^## Prerequisites.*?(?=^## |\Z)', True),
    ],
    'usage.qmd': [
        (r'^## Usage.*?(?=^## |\Z)', True),
    ],
    'contributing.qmd': [
        (r'^## Contributing.*?(?=^## |\Z)', True),
    ],
}


def extract_frontmatter(qmd_path):
    """Extract YAML frontmatter from .qmd file."""
    if not qmd_path.exists():
        return None, None
    
    content = qmd_path.read_text(encoding='utf-8')
    
    # Check for frontmatter (between --- markers)
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        body = frontmatter_match.group(2)
        return frontmatter, body
    
    # No frontmatter found
    return None, content


def extract_readme_sections(readme_content, patterns):
    """Extract matching sections from README.md content."""
    sections = []
    
    for pattern, include_header in patterns:
        matches = re.finditer(pattern, readme_content, re.MULTILINE | re.DOTALL)
        for match in matches:
            section_content = match.group(0)
            # Remove header if not including it (but we always include it)
            sections.append(section_content.strip())
    
    return '\n\n'.join(sections) if sections else None


def extract_readme_title(readme_content):
    """Extract the main title from README.md (first # heading)."""
    # Match the first # heading (main title)
    title_match = re.search(r'^#\s+(.+)$', readme_content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return None


def extract_banner(readme_content):
    """Extract banner image from README.md."""
    # Look for banner image markdown (case-insensitive, flexible spacing)
    banner_match = re.search(r'!\[.*?[Bb]anner.*?\]\([^)]+\)', readme_content, re.IGNORECASE)
    if banner_match:
        banner_line = banner_match.group(0)
        # Convert absolute GitHub URL to relative path for Quarto
        banner_line = re.sub(
            r'\(https://raw\.githubusercontent\.com/[^)]+\)',
            '(assets/dragggB3.png)',
            banner_line
        )
        return banner_line
    return None


def update_qmd_file(qmd_path, readme_content, section_patterns, readme_title=None):
    """Update .qmd file content while preserving frontmatter."""
    # Extract frontmatter
    frontmatter, existing_body = extract_frontmatter(qmd_path)
    
    # Extract sections from README
    new_content = extract_readme_sections(readme_content, section_patterns)
    
    if not new_content:
        print(f"Warning: No matching sections found for {qmd_path.name}")
        return False
    
    # Handle banner image: convert absolute GitHub URL back to relative for Quarto
    new_content = re.sub(
        r'!\[draggg Banner\]\(https://raw\.githubusercontent\.com/[^)]+\)',
        '![draggg Banner](assets/dragggB3.png)',
        new_content
    )
    
    # For index.qmd, add banner at the top
    if qmd_path.name == 'index.qmd':
        banner = extract_banner(readme_content)
        if banner:
            new_content = f"{banner}\n\n{new_content}"
    
    # Update title in frontmatter for index.qmd if title is provided
    if qmd_path.name == 'index.qmd' and readme_title and frontmatter:
        # Update title field in YAML frontmatter
        # Match title: "..." or title: '...'
        frontmatter = re.sub(
            r'^title:\s*["\'].*?["\']',
            f'title: "{readme_title}"',
            frontmatter,
            flags=re.MULTILINE
        )
        # If title field doesn't exist, add it at the beginning
        if 'title:' not in frontmatter:
            frontmatter = f'title: "{readme_title}"\n{frontmatter}'
    
    # Construct new file content
    if frontmatter:
        new_file_content = f"---\n{frontmatter}\n---\n\n{new_content}\n"
    else:
        new_file_content = f"{new_content}\n"
    
    # Write back
    qmd_path.write_text(new_file_content, encoding='utf-8')
    print(f"Updated {qmd_path.name}")
    return True


def update_quarto_config(readme_title):
    """Update _quarto.yml website.title field."""
    quarto_config_path = BASE_DIR / "_quarto.yml"
    
    if not quarto_config_path.exists():
        print(f"Warning: _quarto.yml not found, skipping title update")
        return False
    
    content = quarto_config_path.read_text(encoding='utf-8')
    
    # Update website.title field
    # Match website:\n  title: "..."
    content = re.sub(
        r'(website:\s*\n\s+title:\s*)["\'][^"\']*["\']',
        f'\\1"{readme_title}"',
        content,
        flags=re.MULTILINE
    )
    
    quarto_config_path.write_text(content, encoding='utf-8')
    print(f"Updated _quarto.yml title")
    return True


def main():
    """Main sync function."""
    readme_path = BASE_DIR / "README.md"
    
    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}")
        sys.exit(1)
    
    # Read README.md
    readme_content = readme_path.read_text(encoding='utf-8')
    
    # Extract README title
    readme_title = extract_readme_title(readme_content)
    if readme_title:
        print(f"Extracted README title: {readme_title}")
        # Update _quarto.yml title
        update_quarto_config(readme_title)
    else:
        print("Warning: Could not extract README title")
    
    # Process each .qmd file
    updated_count = 0
    for qmd_filename, section_patterns in SECTION_MAPPINGS.items():
        qmd_path = BASE_DIR / qmd_filename
        
        if not qmd_path.exists():
            print(f"Warning: {qmd_filename} not found, skipping")
            continue
        
        if update_qmd_file(qmd_path, readme_content, section_patterns, readme_title):
            updated_count += 1
    
    print(f"\nSync complete: Updated {updated_count} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
