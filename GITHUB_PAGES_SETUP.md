# GitHub Pages Setup Instructions

## Enable GitHub Pages for Documentation

To make the user documentation website live at `https://gm5dna.github.io/growth-parameters-calculator/`, follow these steps:

### 1. Go to Repository Settings
- Navigate to https://github.com/gm5dna/growth-parameters-calculator
- Click on **Settings** (top menu)

### 2. Configure GitHub Pages
- In the left sidebar, click **Pages** (under "Code and automation")

### 3. Set Source
- Under "Build and deployment"
- **Source:** Select "Deploy from a branch"
- **Branch:** Select `main`
- **Folder:** Select `/docs`
- Click **Save**

### 4. Wait for Deployment
- GitHub will build and deploy the site (usually takes 1-2 minutes)
- A green checkmark will appear when ready
- The URL will be displayed: `https://gm5dna.github.io/growth-parameters-calculator/`

### 5. Verify
- Click the URL or visit https://gm5dna.github.io/growth-parameters-calculator/
- You should see the comprehensive user documentation

## Accessing the Documentation

Once enabled, users can access the documentation:

1. **From the calculator:** Click the "User Guide" link in the top-right corner
2. **Directly:** Visit https://gm5dna.github.io/growth-parameters-calculator/
3. **From GitHub:** The URL will appear in the repository's About section

## Updating Documentation

To update the documentation:

1. Edit files in the `docs/` folder
2. Commit and push changes to the `main` branch
3. GitHub Pages will automatically rebuild and redeploy (1-2 minutes)

## Custom Domain (Optional)

If you want to use a custom domain:

1. In GitHub Pages settings, enter your custom domain
2. Add a CNAME record in your DNS settings pointing to `gm5dna.github.io`
3. Wait for DNS propagation (can take 24-48 hours)

## Troubleshooting

**Site not appearing?**
- Check that GitHub Pages is enabled in Settings > Pages
- Verify the branch is set to `main` and folder to `/docs`
- Wait a few minutes for the build to complete
- Check the Actions tab for build status

**Changes not showing?**
- Clear your browser cache
- Wait 1-2 minutes for GitHub Pages to rebuild
- Check that changes were pushed to the `main` branch

**404 error?**
- Verify the folder is `/docs` (this is a GitHub Pages requirement)
- Ensure `index.html` exists in the `docs/` folder
- Check repository visibility is set to Public

## What's Included

The documentation covers:
- Quick start guide
- Feature overview
- Measurement guidelines
- Understanding results (centiles, SDS)
- Preterm infant calculations
- Advanced features (height velocity, MPH, BSA, GH dosing)
- Growth references
- Tips & best practices
- Clinical disclaimer
- Support links

The documentation is fully responsive, matches the app's theme, and includes dark mode support.
