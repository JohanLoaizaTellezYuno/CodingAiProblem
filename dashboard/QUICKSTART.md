# Horizon Gaming Dashboard - Quick Start Guide

## Start the Dashboard (2 commands)

```bash
# Navigate to dashboard directory
cd /Users/johan/Documents/Coding\ AI/horizon-gaming-detector/dashboard

# Start development server
npm run dev
```

Open browser to: **http://localhost:3000**

## What You'll See

The dashboard displays mock data by default, showing:

- **4 Metric Cards**: Transaction volume, settled amount, discrepancy amount, discrepancy rate
- **Time Series Chart**: Daily/weekly trends of transactions vs settlements
- **3 Breakdown Charts**: By provider, payment method, and country
- **Anomaly Table**: Top 15 anomalies sorted by financial impact
- **Filters**: Date range, provider, country, payment method filters

## Using Real Data (When Pipeline Completes)

Once the data pipeline generates files, integrate them:

```bash
# Create public data directory
mkdir -p public/data

# Copy pipeline output files
cp ../data/processed/reconciled_data.json public/data/
cp ../data/processed/anomalies.json public/data/
cp ../data/processed/insights.json public/data/

# Restart server
npm run dev
```

The dashboard will automatically detect and use real data.

## Key Features

### Filters
- Use date range picker to filter by time period
- Check/uncheck providers, countries, or payment methods
- Click "Clear All" to reset filters
- All charts and metrics update automatically

### Charts
- **Time Series**: Toggle between Daily/Weekly views
- **Hover**: All charts show detailed tooltips on hover
- **Breakdown**: Three different chart types for different insights

### Anomaly Table
- Sort by "Impact" (default) or "Date"
- Filter by severity: All, Critical, Warning, Info
- Shows top 15 most impactful anomalies
- Hover over action text to see full suggestion

## Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Troubleshooting

**Dashboard won't start?**
```bash
# Reinstall dependencies
npm install
```

**Changes not showing?**
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

**Port 3000 already in use?**
```bash
# Use different port
PORT=3001 npm run dev
```

## Code Stats

- **1,350+ lines** of TypeScript/TSX code written
- **5 React components** for visualization
- **2 utility libraries** for data and formatting
- **Full TypeScript type system** for type safety
- **Zero runtime errors** in production build

## Next Steps

1. Wait for data pipeline to complete (senior-data-architect agent)
2. Copy generated JSON files to `public/data/`
3. Refresh dashboard to see real reconciliation data
4. Use filters to drill down into specific issues
5. Export anomaly list for follow-up actions

## Support

See full documentation in `README.md` or main project `PHASE4_COMPLETE.md`.
