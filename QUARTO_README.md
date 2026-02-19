# Quarto Documentation Setup

This project uses [Quarto](https://quarto.org/) to generate beautiful documentation websites.

## Setup

1. **Install Quarto:**
   ```bash
   # Follow instructions at: https://quarto.org/docs/get-started/
   ```

2. **Build the documentation:**
   ```bash
   ./build_quarto.sh
   # Or manually:
   quarto render
   ```

3. **Preview locally:**
   ```bash
   quarto preview
   ```

## Publishing to GitHub Pages

The documentation can be published to GitHub Pages:

1. **Enable GitHub Pages** in repository settings:
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` / `docs` folder

2. **Or use GitHub Actions** (recommended):
   - Create `.github/workflows/quarto-publish.yml`
   - The workflow will build and deploy on push

## File Structure

- `_quarto.yml` - Quarto project configuration
- `index.qmd` - Home page
- `installation.qmd` - Installation guide
- `usage.qmd` - Usage documentation
- `contributing.qmd` - Contributing guide
- `styles.css` - Custom CSS styles
- `docs/` - Generated HTML output (gitignored)

## Updating Documentation

1. Edit the `.qmd` files
2. Run `quarto render` to rebuild
3. Commit and push changes
4. Documentation will update automatically if GitHub Pages is configured
