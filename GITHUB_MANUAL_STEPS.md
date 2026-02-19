# GitHub Manual Setup Guide

## Files Already Created (Reference)

The following files are already in your repository and don't need manual setup:

### GitHub Actions Workflows
- `.github/workflows/publish.yml` - PyPI publishing on tags
- `.github/workflows/quarto-publish.yml` - Documentation publishing

### Quarto Documentation Files
- `_quarto.yml` - Quarto configuration
- `index.qmd` - Home page
- `installation.qmd` - Installation guide
- `usage.qmd` - Usage documentation
- `contributing.qmd` - Contributing guide
- `styles.css` - Custom styles
- `build_quarto.sh` - Build script

### Documentation
- `GITHUB_SETUP.md` - General setup guide
- `QUARTO_README.md` - Quarto documentation guide

## Manual Steps Required in GitHub

### Step 1: Add PyPI API Token as GitHub Secret

**Purpose:** Allow GitHub Actions to publish packages to PyPI

**Steps:**
1. Navigate to your repository: `https://github.com/j031nich0145/draggg`
2. Click on **Settings** tab (top navigation bar)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click the **New repository secret** button (top right)
5. Fill in the form:
   - **Name:** `PYPI_API_TOKEN`
   - **Secret:** Paste your PyPI API token (get it from https://pypi.org/manage/account/token/)
6. Click **Add secret**
7. Verify the secret appears in the list (it will show as `PYPI_API_TOKEN` with masked value)

**Verification:**
- The secret should appear in the secrets list
- You can edit or delete it later if needed

### Step 2: Enable GitHub Pages

**Purpose:** Publish Quarto documentation site automatically

**Steps:**
1. Still in **Settings** tab
2. In the left sidebar, click **Pages**
3. Under **Source**, select **GitHub Actions** (not "Deploy from a branch")
4. The page will show: "Your site is ready to be published"
5. No further action needed - the workflow will deploy automatically

**Note:** After the first push to main, GitHub Pages will be automatically configured and your site will be available at:
`https://j031nich0145.github.io/draggg/`

### Step 3: Verify Workflows Are Active

**Purpose:** Ensure GitHub Actions workflows are enabled

**Steps:**
1. Click on **Actions** tab (top navigation bar)
2. You should see two workflows listed:
   - **Publish to PyPI** - Publishes packages on tags
   - **Publish Quarto Site** - Publishes documentation on push to main
3. If workflows are disabled (grayed out), click on the workflow name
4. Click **Enable workflow** button if prompted

**Verification:**
- Both workflows should show as enabled
- You can see their run history (will be empty until first trigger)

### Step 4: Test PyPI Publishing (Optional - After First Tag)

**Purpose:** Verify tag-based publishing works

**Steps:**
1. After creating and pushing a version tag (e.g., `v1.0.1`)
2. Go to **Actions** tab
3. You should see a workflow run named "Publish to PyPI"
4. Click on it to see the build progress
5. Wait for it to complete (green checkmark)
6. Verify on PyPI: `https://pypi.org/project/draggg/`

**What to look for:**
- Workflow starts automatically when tag is pushed
- Build step completes successfully
- Upload step completes successfully
- Package appears on PyPI within a few minutes

### Step 5: Test Documentation Publishing (Optional - After First Push)

**Purpose:** Verify Quarto documentation builds and deploys

**Steps:**
1. After pushing changes to `main` branch
2. Go to **Actions** tab
3. You should see a workflow run named "Publish Quarto Site"
4. Click on it to see the build progress
5. Wait for it to complete (green checkmark)
6. Go to **Settings** → **Pages** to see deployment status
7. Visit your site: `https://j031nich0145.github.io/draggg/`

**What to look for:**
- Workflow starts automatically on push to main
- Quarto render step completes
- Pages deployment completes
- Site is accessible at the GitHub Pages URL

## Quick Reference Checklist

- [ ] Added `PYPI_API_TOKEN` secret in Settings → Secrets and variables → Actions
- [ ] Enabled GitHub Pages in Settings → Pages (Source: GitHub Actions)
- [ ] Verified workflows are enabled in Actions tab
- [ ] (Optional) Tested tag-based publishing with a version tag
- [ ] (Optional) Verified documentation site is accessible

## Troubleshooting

### Workflow Not Running
- Check that workflows are enabled in Actions tab
- Verify branch protection rules aren't blocking workflows
- Check repository settings allow GitHub Actions

### PyPI Upload Fails
- Verify `PYPI_API_TOKEN` secret is correctly named and set
- Check token hasn't expired (create new one if needed)
- Verify token has correct permissions (should be account-wide or project-scoped)

### Documentation Not Publishing
- Verify GitHub Pages is enabled (Settings → Pages)
- Check workflow completed successfully in Actions tab
- Wait a few minutes for DNS propagation
- Clear browser cache if site doesn't update

## Next Steps After Setup

1. **Create your first version tag:**
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

2. **Push to main to trigger documentation build:**
   ```bash
   git push origin main
   ```

3. **Monitor workflows in Actions tab** to ensure everything works

## Support

If you encounter issues:
- Check workflow logs in Actions tab for error messages
- Verify all secrets are set correctly
- Ensure repository permissions allow GitHub Actions
- Check GitHub status page for service issues

**Note:** For local publishing, use `.env.example` as a template. Copy it to `.env` and add your token. Never commit `.env` to git!
