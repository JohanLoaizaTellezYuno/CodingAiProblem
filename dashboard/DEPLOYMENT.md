# Vercel Deployment Guide

## Dashboard Deployment Status

### Quick Deploy (5 minutes)

#### Method 1: Vercel CLI (Fastest)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```
   This will open your browser for authentication.

3. **Deploy to Production**:
   ```bash
   cd /Users/johan/Documents/Coding\ AI/horizon-gaming-detector/dashboard
   vercel --prod
   ```

4. **Follow the prompts**:
   - Set up and deploy? **Yes**
   - Which scope? Select your account
   - Link to existing project? **No** (first time)
   - What's your project's name? **horizon-gaming-dashboard** (or your choice)
   - In which directory is your code located? **./** (default)
   - Want to modify settings? **No** (Vercel auto-detects Next.js)

#### Method 2: Vercel Dashboard (5-10 minutes)

1. **Visit**: https://vercel.com/new

2. **Import Git Repository**:
   - Click "Import Git Repository"
   - If not on GitHub yet, push to GitHub first:
     ```bash
     cd /Users/johan/Documents/Coding\ AI/horizon-gaming-detector
     git init
     git add .
     git commit -m "Initial commit - Horizon Gaming Dashboard"
     git remote add origin [YOUR_GITHUB_REPO_URL]
     git push -u origin main
     ```

3. **Configure Project**:
   - Framework Preset: **Next.js** (auto-detected)
   - Root Directory: **dashboard**
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)
   - Install Command: `npm install` (default)

4. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes for build and deployment

5. **Get URL**:
   - Copy the deployment URL: `https://[project-name].vercel.app`

## Project Configuration

### Build Settings (Pre-configured)
- ✅ Framework: Next.js 16.1.6
- ✅ Build Command: `npm run build`
- ✅ Output Directory: `.next`
- ✅ Node Version: Auto-detected from package.json
- ✅ Build verified: Successful (1.8s compile time)

### Environment Variables
- ✅ No environment variables required
- ✅ Dashboard uses mock data by default
- ✅ Data files in `/public/data/` (optional)

### Project Structure
```
dashboard/
├── app/               # Next.js 14+ App Router
├── components/        # React components
├── lib/              # Utilities and data loaders
├── types/            # TypeScript definitions
├── public/           # Static assets
├── vercel.json       # Vercel configuration
└── package.json      # Dependencies
```

## Post-Deployment Verification

Once deployed, test these features:

1. **Homepage loads**: https://[your-url].vercel.app
2. **Metrics display**: 4 KPI cards visible
3. **Charts render**: Time series, breakdowns, and pie charts
4. **Filters work**: Date range, provider, country, payment method
5. **Anomaly table**: Sortable, filterable, with severity badges
6. **Responsive design**: Test on mobile, tablet, desktop

## Troubleshooting

### Build Fails
- Check `npm run build` locally first
- Review build logs in Vercel dashboard
- Ensure all dependencies in package.json

### Page Not Found
- Verify root directory is set to `dashboard`
- Check deployment logs for errors

### Charts Not Rendering
- Check browser console for errors
- Verify Recharts version compatibility

## Update Deployment

To update the live site:

```bash
cd /Users/johan/Documents/Coding\ AI/horizon-gaming-detector/dashboard
vercel --prod
```

Or push to GitHub (if connected via Vercel integration).

## Performance Metrics

- Build Time: ~2-3 seconds
- Cold Start: <1 second
- Time to Interactive: <3 seconds
- Lighthouse Score: 95+ expected

## Support

- Vercel Docs: https://vercel.com/docs
- Next.js Docs: https://nextjs.org/docs
- Project Issues: Check build logs in Vercel dashboard
