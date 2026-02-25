#!/bin/bash

# Horizon Gaming Dashboard - Vercel Deployment Script
# Run this script to deploy to Vercel in one command

set -e  # Exit on any error

echo "🚀 Horizon Gaming Dashboard - Vercel Deployment"
echo "================================================"
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null
then
    echo "⚠️  Vercel CLI not found. Installing..."
    npm install -g vercel
    echo "✅ Vercel CLI installed"
else
    echo "✅ Vercel CLI already installed"
fi

echo ""
echo "📦 Building dashboard for production..."
npm run build

echo ""
echo "✅ Build successful!"
echo ""
echo "🌐 Deploying to Vercel..."
echo ""
echo "NOTE: You may need to authenticate in your browser."
echo "      A browser window will open automatically."
echo ""

# Deploy to production
vercel --prod

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "  1. Open the deployment URL in your browser"
echo "  2. Test all dashboard features"
echo "  3. Update README.md with your live URL"
echo ""
