# GitHub Actions CI/CD Workflows

This directory contains automated workflows for testing and deployment.

## Workflows

### 1. Test Workflow (`test.yml`)

**Triggers:**
- Push to `main` branch
- Pull requests targeting `main` branch

**Jobs:**
- **Python Tests**: Runs pytest with coverage reporting
- **Dashboard Build**: Validates Next.js dashboard builds successfully
- **Linting**: Runs ESLint on dashboard code

**Requirements:**
- Python 3.9
- Node.js 18
- All dependencies from `requirements.txt` and `dashboard/package.json`

### 2. Deploy Workflow (`deploy.yml`)

**Triggers:**
- Push to `main` branch only

**Jobs:**
- **Deploy**: Deploys dashboard to Vercel production
- **Tag Release**: Creates automatic version tags (format: `vYYYY.MM.DD-N`)

**Required Secrets:**
You need to add the following secret to your GitHub repository:

1. `VERCEL_TOKEN` - Your Vercel deployment token
   - Get it from: https://vercel.com/account/tokens
   - Add it in: Repository Settings → Secrets and variables → Actions → New repository secret

**How to set up Vercel deployment:**

```bash
# Install Vercel CLI
npm install -g vercel

# Link your project (run in dashboard directory)
cd dashboard
vercel link

# Get your Vercel token
# Go to https://vercel.com/account/tokens
# Create a new token and add it as VERCEL_TOKEN secret in GitHub
```

## Testing Locally

### Python Tests
```bash
pip install -r requirements.txt
pytest tests/ --cov=. --cov-report=term
```

### Dashboard Build
```bash
cd dashboard
npm install
npm run build
npm run lint
```

## Workflow Status

Check the status of workflows in the "Actions" tab of your GitHub repository.

## Troubleshooting

**Test workflow fails:**
- Check Python dependencies are correctly installed
- Ensure all tests pass locally before pushing
- Verify Node.js build completes without errors

**Deploy workflow fails:**
- Verify `VERCEL_TOKEN` secret is set correctly
- Check Vercel project is linked
- Ensure Vercel has proper permissions

## Next Steps

1. Add `VERCEL_TOKEN` to repository secrets
2. Push code to trigger workflows
3. Monitor workflow execution in GitHub Actions tab
4. View deployed dashboard on Vercel
