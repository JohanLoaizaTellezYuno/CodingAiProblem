'use client';

import { useState } from 'react';
import { Anomaly } from '@/types';
import { formatCurrency, formatDate, getSeverityColor } from '@/lib/utils';

interface AnomalyFeedProps {
  anomalies: Anomaly[];
}

export default function AnomalyFeed({ anomalies }: AnomalyFeedProps) {
  const [sortBy, setSortBy] = useState<'discrepancy' | 'date'>('discrepancy');
  const [filterSeverity, setFilterSeverity] = useState<'all' | 'critical' | 'warning' | 'info'>('all');

  const filteredAnomalies = anomalies
    .filter(a => filterSeverity === 'all' || a.severity === filterSeverity)
    .sort((a, b) => {
      if (sortBy === 'discrepancy') {
        return b.discrepancy - a.discrepancy;
      }
      return new Date(b.date).getTime() - new Date(a.date).getTime();
    })
    .slice(0, 15);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">Top Anomalies</h2>
        <div className="flex gap-3">
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Severity</option>
            <option value="critical">Critical</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="discrepancy">Sort by Impact</option>
            <option value="date">Sort by Date</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severity
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Provider
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Method
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Country
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Discrepancy
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Action
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredAnomalies.map((anomaly) => (
              <tr key={anomaly.anomaly_id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getSeverityColor(anomaly.severity)}`}>
                    {anomaly.severity.toUpperCase()}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(anomaly.date)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                  {anomaly.provider}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {anomaly.payment_method.replace('_', ' ')}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {anomaly.country}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  <span className="inline-flex items-center">
                    {getAnomalyIcon(anomaly.anomaly_type)}
                    <span className="ml-1">
                      {anomaly.anomaly_type.replace('_', ' ')}
                    </span>
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 font-medium">
                  {formatCurrency(anomaly.amount)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-semibold text-red-600">
                  {formatCurrency(anomaly.discrepancy)}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500 max-w-xs truncate" title={anomaly.suggested_action}>
                  {anomaly.suggested_action}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredAnomalies.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No anomalies found with the selected filters.</p>
        </div>
      )}

      <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
        <p>Showing top {filteredAnomalies.length} of {anomalies.length} anomalies</p>
        <p className="font-semibold">
          Total Impact: {formatCurrency(filteredAnomalies.reduce((sum, a) => sum + a.discrepancy, 0))}
        </p>
      </div>
    </div>
  );
}

function getAnomalyIcon(type: string): string {
  switch (type) {
    case 'missing_settlement':
      return '❌';
    case 'fee_discrepancy':
      return '💰';
    case 'timing_delay':
      return '⏱️';
    case 'ghost_settlement':
      return '👻';
    default:
      return '⚠️';
  }
}
