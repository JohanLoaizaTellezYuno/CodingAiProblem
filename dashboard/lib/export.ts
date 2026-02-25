/**
 * Export Utilities for Horizon Gaming Dashboard
 *
 * Provides CSV export functionality for anomalies and reconciled data.
 */

import { Anomaly, ReconciledRecord } from '@/types';

/**
 * Convert array of objects to CSV string
 */
function objectArrayToCSV<T extends Record<string, any>>(data: T[]): string {
  if (data.length === 0) return '';

  // Get headers from first object
  const headers = Object.keys(data[0]);

  // Create CSV header row
  const csvHeaders = headers.join(',');

  // Create CSV data rows
  const csvRows = data.map(row => {
    return headers.map(header => {
      const value = row[header];

      // Handle null/undefined
      if (value === null || value === undefined) return '';

      // Handle strings with commas or quotes - wrap in quotes and escape existing quotes
      if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
        return `"${value.replace(/"/g, '""')}"`;
      }

      return value;
    }).join(',');
  });

  return [csvHeaders, ...csvRows].join('\n');
}

/**
 * Trigger browser download of CSV file
 */
function downloadCSV(csvContent: string, filename: string): void {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');

  if (link.download !== undefined) {
    // Create download link
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';

    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up
    URL.revokeObjectURL(url);
  }
}

/**
 * Export anomalies to CSV
 */
export function exportAnomaliesToCSV(anomalies: Anomaly[]): void {
  // Format anomalies for export
  const exportData = anomalies.map(a => ({
    Anomaly_ID: a.anomaly_id,
    Transaction_ID: a.transaction_id,
    Date: a.date,
    Provider: a.provider,
    Payment_Method: a.payment_method,
    Country: a.country,
    Anomaly_Type: a.anomaly_type,
    Category: a.category,
    Amount: a.amount,
    Currency: a.currency,
    Amount_USD: a.amount_usd,
    Severity: a.severity,
    Suggested_Action: a.suggested_action,
  }));

  const csvContent = objectArrayToCSV(exportData);
  const timestamp = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const filename = `horizon-gaming-anomalies-${timestamp}.csv`;

  downloadCSV(csvContent, filename);
}

/**
 * Export reconciled transactions to CSV
 */
export function exportReconciledDataToCSV(transactions: ReconciledRecord[]): void {
  // Format transactions for export
  const exportData = transactions.map(t => ({
    Transaction_ID: t.transaction_id,
    Timestamp: t.timestamp,
    Amount: t.amount,
    Currency: t.currency,
    Status: t.status,
    Provider: t.provider,
    Payment_Method: t.payment_method,
    Country: t.country,
    Expected_Settled_Amount: t.expected_settled_amount,
    Actual_Settled_Amount: t.actual_settled_amount || '',
    Discrepancy_Amount: t.discrepancy_amount || '',
    Settlement_Status: t.settlement_status,
    Settlement_Date: t.settlement_date || '',
    Days_To_Settle: t.days_to_settle || '',
    Timing_Anomaly: t.timing_anomaly,
  }));

  const csvContent = objectArrayToCSV(exportData);
  const timestamp = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const filename = `horizon-gaming-reconciled-data-${timestamp}.csv`;

  downloadCSV(csvContent, filename);
}

/**
 * Export metrics summary to CSV
 */
export function exportMetricsToCSV(metrics: {
  totalTransactions: number;
  totalVolume: number;
  totalDiscrepancy: number;
  discrepancyPercentage: number;
}): void {
  const exportData = [
    { Metric: 'Total Transactions', Value: metrics.totalTransactions },
    { Metric: 'Total Volume (USD)', Value: metrics.totalVolume.toFixed(2) },
    { Metric: 'Total Discrepancy (USD)', Value: metrics.totalDiscrepancy.toFixed(2) },
    { Metric: 'Discrepancy Percentage', Value: `${metrics.discrepancyPercentage.toFixed(2)}%` },
  ];

  const csvContent = objectArrayToCSV(exportData);
  const timestamp = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const filename = `horizon-gaming-metrics-${timestamp}.csv`;

  downloadCSV(csvContent, filename);
}
