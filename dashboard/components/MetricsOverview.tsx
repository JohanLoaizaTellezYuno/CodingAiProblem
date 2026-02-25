'use client';

import { AggregateMetrics } from '@/types';
import { formatCurrency, formatNumber, formatPercentage, getStatusColor } from '@/lib/utils';

interface MetricsOverviewProps {
  metrics: AggregateMetrics;
}

export default function MetricsOverview({ metrics }: MetricsOverviewProps) {
  const statusColor = getStatusColor(metrics.discrepancy_percentage);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <MetricCard
        title="Total Transaction Volume"
        value={formatNumber(metrics.total_transaction_volume)}
        subtitle={formatCurrency(metrics.total_transaction_amount)}
        icon="📊"
      />

      <MetricCard
        title="Total Settled Amount"
        value={formatCurrency(metrics.total_settled_amount)}
        subtitle={`${formatNumber(metrics.total_transaction_volume - metrics.unmatched_count)} transactions`}
        icon="✅"
      />

      <MetricCard
        title="Total Discrepancy"
        value={formatCurrency(metrics.total_discrepancy_amount)}
        subtitle={`${metrics.unmatched_count} unmatched transactions`}
        icon="⚠️"
        alert
      />

      <MetricCard
        title="Discrepancy Rate"
        value={formatPercentage(metrics.discrepancy_percentage)}
        subtitle={`${metrics.timing_anomalies_count} timing anomalies`}
        icon="📈"
        statusColor={statusColor}
      />
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  subtitle: string;
  icon: string;
  alert?: boolean;
  statusColor?: string;
}

function MetricCard({ title, value, subtitle, icon, alert, statusColor }: MetricCardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 border-2 transition-all hover:shadow-lg ${
      alert ? 'border-red-200' : 'border-gray-100'
    }`}>
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        <span className="text-2xl">{icon}</span>
      </div>
      <div className={`text-3xl font-bold mb-1 ${statusColor ? statusColor.split(' ')[0] : 'text-gray-900'}`}>
        {value}
      </div>
      <p className="text-sm text-gray-500">{subtitle}</p>
    </div>
  );
}
