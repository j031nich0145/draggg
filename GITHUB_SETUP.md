# GitHub Setup Guide

## Tag-Based PyPI Publishing

The repository is configured to automatically publish to PyPI when you create a version tag.

### How It Works

1. **Update version numbers** in `setup.py` and `pyproject.toml`
2. **Create a git tag** with version number (e.g., `v1.0.1`)
3. **Push the tag** to GitHub
4. **GitHub Actions** automatically builds and publishes to PyPI

### Steps to Publish a New Version

1. **Update version numbers:**
   ```bash
   # Edit setup.py - change version="1.0.0" to version="1.0.1"
   # Edit pyproject.toml - change version = "1.0.0" to version = "1.0.1"
   ```

2. **Commit your changes:**
   ```bash
   git add setup.py pyproject.toml
   git commit -m "Bump version to 1.0.1"
   ```

3. **Create and push the tag:**
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

4. **GitHub Actions will automatically:**
   - Build the package
   - Upload to PyPI
   - You can watch progress in the Actions tab

### Manual Trigger

You can also manually trigger the workflow:
- Go to Actions → "Publish to PyPI" workflow
- Click "Run workflow" → "Run workflow"

### Prerequisites

Make sure you've added your PyPI API token as a GitHub Secret:
- Go to Settings → Secrets and variables → Actions
- Add secret named `PYPI_API_TOKEN` with your PyPI token

## Quarto Documentation

The project includes Quarto documentation that can be published to GitHub Pages.

### Building Locally

```bash
# Install Quarto first: https://quarto.org/docs/get-started/
./build_quarto.sh
quarto preview  # Preview locally
```

### Publishing to GitHub Pages

The documentation is automatically published via GitHub Actions when you push to main.

To enable manually:
1. Go to Settings → Pages
2. Source: GitHub Actions

The workflow (`.github/workflows/quarto-publish.yml`) will build and deploy automatically.

## Workflows Summary

- **`.github/workflows/publish.yml`** - Publishes to PyPI on tags
- **`.github/workflows/quarto-publish.yml`** - Publishes documentation to GitHub Pages

Both workflows run automatically when triggered!
