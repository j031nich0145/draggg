# Publishing draggg to PyPI

## Option 1: GitHub Actions Workflow (Recommended)

The repository includes a GitHub Actions workflow that automatically publishes to PyPI when you create a GitHub release.

### Setup

1. **Add PyPI API Token to GitHub Secrets:**
   - Go to your repository: https://github.com/j031nich0145/draggg
   - Navigate to: Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token (from https://pypi.org/manage/account/token/)
   - Click "Add secret"

2. **Publish a Release:**
   - Create a new release on GitHub (Releases → Draft a new release)
   - Tag version (e.g., `v1.0.0`)
   - Release title (e.g., `draggg 1.0.0`)
   - Publish the release
   - The workflow will automatically build and publish to PyPI

### Manual Trigger

You can also manually trigger the workflow:
- Go to Actions tab → "Publish to PyPI" workflow
- Click "Run workflow" → "Run workflow"

## Option 2: Local Publishing Script

Use the provided `publish.sh` script:

```bash
./publish.sh
```

This script:
1. Builds the package (`python3 -m build`)
2. Reads credentials from `.env` file
3. Uploads to PyPI using twine

**Setup `.env` file:**
1. Copy the template: `cp .env.example .env`
2. Edit `.env` and add your PyPI API token:
   ```ini
   [pypi]
   username = __token__
   password = your-pypi-api-token-here
   ```
3. **Important:** Never commit `.env` to git - it's already in `.gitignore`

## Option 3: Manual Upload

```bash
# Build the package
python3 -m build

# Upload to PyPI
python3 -m twine upload dist/*
```

You'll be prompted for credentials, or you can use environment variables:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-pypi-api-token
python3 -m twine upload dist/*
```

## Getting Your PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Log in to your PyPI account
3. Click "Add API token"
4. Name it (e.g., "draggg-upload")
5. Scope: "Entire account" or "Project: draggg"
6. Click "Add token"
7. Copy the token (shown only once!)

## Security Notes

- **Never commit `.env` to git** - it's already in `.gitignore`
- **Use `.env.example` as a template** - copy it to `.env` and fill in your credentials
- **Use GitHub Secrets** for CI/CD workflows (more secure than hardcoding)
- **API tokens** are preferred over passwords
- **Project-scoped tokens** are more secure than account-wide tokens
