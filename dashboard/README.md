# Horizon Gaming Revenue Anomaly Detector - Dashboard

A Next.js 14 dashboard for visualizing revenue anomalies and settlement reconciliation data for Horizon Gaming's payment processing operations across Latin America.

## Live Demo

**Deployment Ready** - Follow the [Deployment Guide](DEPLOYMENT.md) to deploy to Vercel in 5 minutes.

Once deployed, your live URL will be: `https://[your-project-name].vercel.app`

## Features

- **Real-time Metrics Overview**: Display key metrics including transaction volume, settled amounts, discrepancies, and rates
- **Time Series Visualization**: Interactive charts showing daily/weekly transaction trends vs settlement amounts
- **Breakdown Analysis**: Three-way breakdown by provider, payment method, and country
- **Anomaly Feed**: Sortable and filterable list of top anomalies ranked by financial impact
- **Advanced Filtering**: Filter all data by date range, provider, country, and payment method
- **Responsive Design**: Professional UI optimized for desktop viewing
- **Mock Data Support**: Works with mock data during development, seamlessly integrates with real data

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Date Handling**: date-fns

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Installation

1. Install dependencies:

```bash
npm install
```

### Running the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to view the dashboard.

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
dashboard/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout with metadata
│   ├── page.tsx           # Main dashboard page
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── MetricsOverview.tsx      # Key metrics cards
│   ├── TimeSeriesChart.tsx      # Transaction trends chart
│   ├── BreakdownCharts.tsx      # Provider/method/country charts
│   ├── AnomalyFeed.tsx          # Anomaly list table
│   └── Filters.tsx              # Filter controls
├── lib/                   # Utilities and data loading
│   ├── data.ts           # Data fetching and mock data generation
│   └── utils.ts          # Formatting and helper functions
├── types/                 # TypeScript type definitions
│   └── index.ts          # All type definitions
└── public/               # Static assets
```

## Data Integration

The dashboard is designed to work with both mock data (for development) and real data from the pipeline.

### Mock Data (Default)

When real data files are not available, the dashboard automatically generates realistic mock data including:
- 800 transaction records
- 50 anomalies with various severity levels
- Aggregate insights and metrics
- Time series data over 30 days

### Real Data Integration

To use real data from the pipeline:

1. Ensure the data pipeline has generated files in `../data/processed/`:
   - `reconciled_data.json` or `reconciled_data.csv`
   - `anomalies.json`
   - `insights.json`

2. Place these files in the `dashboard/public/data/` directory:

```bash
mkdir -p public/data
cp ../data/processed/reconciled_data.json public/data/
cp ../data/processed/anomalies.json public/data/
cp ../data/processed/insights.json public/data/
```

3. The dashboard will automatically detect and use the real data files.

## Component Overview

### MetricsOverview

Displays four key metric cards:
- Total Transaction Volume (count + amount)
- Total Settled Amount
- Total Discrepancy Amount
- Discrepancy Rate (with color-coded status)

### TimeSeriesChart

Interactive chart with:
- Daily/weekly view toggle
- Transaction amount line (blue)
- Settled amount line (green)
- Transaction volume bars (light blue)
- Responsive tooltips

### BreakdownCharts

Three visualization panels:
1. **Provider Breakdown**: Horizontal bar chart of discrepancies by provider
2. **Payment Method Breakdown**: Pie chart of discrepancy rates by method
3. **Country Breakdown**: Grouped bar chart comparing volume vs discrepancy

### AnomalyFeed

Comprehensive anomaly table with:
- Sortable columns (by impact or date)
- Severity filtering (critical/warning/info)
- Color-coded severity badges
- Truncated action suggestions with hover tooltips
- Shows top 15 anomalies

### Filters

Multi-select filters for:
- Date range (start/end dates)
- Providers (checkbox list)
- Countries (checkbox list)
- Payment methods (checkbox list)

All filters dynamically update all dashboard components.

## Customization

### Branding

Update branding in `/app/page.tsx`:
- Header title and subtitle
- Color scheme (currently blue gradient)
- Footer text

### Styling

Modify Tailwind configuration in `tailwind.config.ts` and global styles in `app/globals.css`.

### Data Thresholds

Adjust discrepancy thresholds in `lib/utils.ts`:

```typescript
export function getStatusColor(percentage: number): string {
  if (percentage < 2) return 'text-green-600 bg-green-50'; // Good
  if (percentage < 5) return 'text-yellow-600 bg-yellow-50'; // Warning
  return 'text-red-600 bg-red-50'; // Critical
}
```

## Performance

- Initial load time: <3 seconds with mock data
- Data processing: Client-side filtering for <1000 records
- Chart rendering: Optimized with Recharts lazy loading
- Responsive design: Breakpoints at 768px (md) and 1024px (lg)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Dashboard shows loading spinner indefinitely

Check browser console for errors. Ensure all dependencies are installed:

```bash
npm install
```

### Charts not rendering

Verify Recharts is installed:

```bash
npm install recharts
```

### TypeScript errors

Ensure TypeScript types are correctly defined in `types/index.ts` and match data structures.

## Future Enhancements

- CSV export functionality for anomaly list
- PDF report generation for executive summary
- Real-time data updates via WebSocket
- Historical comparison view
- Provider-specific drill-down pages
- Mobile-optimized responsive design

## License

MIT

## Support

For issues or questions, contact the development team or refer to the main project README.
