import { ReconciledRecord, Anomaly, Insight, TimeSeriesData, AggregateMetrics } from '@/types';

// Mock data generator for development
function generateMockReconciledData(): ReconciledRecord[] {
  const providers = ['PayBridge', 'LatamPay', 'GlobalSettle', 'FastPay', 'VoucherPro'];
  const countries = ['Brazil', 'Mexico', 'Colombia', 'Chile'];
  const paymentMethods: Array<'credit_card' | 'debit_card' | 'bank_transfer' | 'cash_voucher'> = [
    'credit_card', 'debit_card', 'bank_transfer', 'cash_voucher'
  ];
  const statuses: Array<'approved' | 'captured' | 'declined' | 'pending' | 'refunded' | 'chargedback'> = [
    'approved', 'captured', 'declined', 'pending', 'refunded', 'chargedback'
  ];
  const currencies = ['BRL', 'MXN', 'COP', 'CLP'];
  const settlementStatuses: Array<'matched' | 'missing' | 'discrepancy' | 'ghost'> = [
    'matched', 'missing', 'discrepancy', 'ghost'
  ];

  const records: ReconciledRecord[] = [];
  const now = new Date();

  for (let i = 0; i < 800; i++) {
    const daysAgo = Math.floor(Math.random() * 30);
    const timestamp = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000);
    const amount = Math.random() * 5000 + 10;
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const settlementStatus = settlementStatuses[Math.floor(Math.random() * settlementStatuses.length)];
    const hasSettlement = status === 'captured' && Math.random() > 0.2;
    const feePercent = 0.029;
    const feeFixed = 0.30;
    const expectedSettled = amount - (amount * feePercent + feeFixed);
    const actualSettled = hasSettlement ? expectedSettled + (Math.random() - 0.5) * 50 : null;
    const daysToSettle = hasSettlement ? Math.floor(Math.random() * 10) + 1 : null;

    records.push({
      transaction_id: `TXN_${String(i + 1).padStart(5, '0')}`,
      timestamp: timestamp.toISOString(),
      amount,
      currency: currencies[Math.floor(Math.random() * currencies.length)],
      status,
      provider: providers[Math.floor(Math.random() * providers.length)],
      payment_method: paymentMethods[Math.floor(Math.random() * paymentMethods.length)],
      country: countries[Math.floor(Math.random() * countries.length)],
      customer_id: `CUST_${String(Math.floor(Math.random() * 500) + 1).padStart(5, '0')}`,
      settlement_id: hasSettlement ? `SET_${String(i + 1).padStart(5, '0')}` : null,
      settlement_date: hasSettlement ? new Date(timestamp.getTime() + (daysToSettle || 3) * 24 * 60 * 60 * 1000).toISOString() : null,
      expected_settled_amount: expectedSettled,
      actual_settled_amount: actualSettled,
      settlement_status: hasSettlement ? settlementStatus : 'missing',
      timing_anomaly: hasSettlement && (daysToSettle || 0) > 7,
      discrepancy_amount: actualSettled ? Math.abs(expectedSettled - actualSettled) : amount,
      days_to_settle: daysToSettle,
    });
  }

  return records;
}

function generateMockAnomalies(records: ReconciledRecord[]): Anomaly[] {
  const anomalies: Anomaly[] = [];

  records
    .filter(r => r.settlement_status !== 'matched' || r.timing_anomaly)
    .slice(0, 50)
    .forEach((record, index) => {
      const anomalyType = record.settlement_status === 'missing' ? 'missing_settlement' :
                          record.settlement_status === 'discrepancy' ? 'fee_discrepancy' :
                          record.timing_anomaly ? 'timing_delay' : 'ghost_settlement';

      const severity: 'critical' | 'warning' | 'info' =
        record.discrepancy_amount > 1000 ? 'critical' :
        record.discrepancy_amount > 100 ? 'warning' : 'info';

      anomalies.push({
        anomaly_id: `ANO_${String(index + 1).padStart(5, '0')}`,
        transaction_id: record.transaction_id,
        date: record.timestamp,
        provider: record.provider,
        payment_method: record.payment_method,
        country: record.country,
        anomaly_type: anomalyType,
        category: anomalyType.replace('_', ' '),
        amount: record.amount,
        expected_amount: record.expected_settled_amount,
        discrepancy: record.discrepancy_amount,
        severity,
        suggested_action: getSuggestedAction(anomalyType, record.provider),
      });
    });

  return anomalies.sort((a, b) => b.discrepancy - a.discrepancy);
}

function getSuggestedAction(anomalyType: string, provider: string): string {
  switch (anomalyType) {
    case 'missing_settlement':
      return `Contact ${provider} to investigate missing settlements`;
    case 'fee_discrepancy':
      return `Review fee agreement with ${provider} for unexpected charges`;
    case 'timing_delay':
      return `Escalate delayed settlements for transactions >7 days old`;
    case 'ghost_settlement':
      return `Reconcile ghost settlement with ${provider} transaction records`;
    default:
      return 'Review transaction details';
  }
}

function generateMockInsights(records: ReconciledRecord[], anomalies: Anomaly[]): Insight {
  const totalAmount = records.reduce((sum, r) => sum + r.amount, 0);
  const totalSettled = records.reduce((sum, r) => sum + (r.actual_settled_amount || 0), 0);
  const totalDiscrepancy = records.reduce((sum, r) => sum + r.discrepancy_amount, 0);

  // Provider analysis
  const providerMap = new Map<string, { volume: number; discrepancy: number }>();
  records.forEach(r => {
    const current = providerMap.get(r.provider) || { volume: 0, discrepancy: 0 };
    providerMap.set(r.provider, {
      volume: current.volume + r.amount,
      discrepancy: current.discrepancy + r.discrepancy_amount,
    });
  });

  const providerAnalysis = Array.from(providerMap.entries()).map(([provider, data]) => ({
    provider,
    total_volume: data.volume,
    discrepancy_rate: (data.discrepancy / data.volume) * 100,
    discrepancy_amount: data.discrepancy,
  }));

  // Method analysis
  const methodMap = new Map<string, { volume: number; discrepancy: number }>();
  records.forEach(r => {
    const current = methodMap.get(r.payment_method) || { volume: 0, discrepancy: 0 };
    methodMap.set(r.payment_method, {
      volume: current.volume + r.amount,
      discrepancy: current.discrepancy + r.discrepancy_amount,
    });
  });

  const methodAnalysis = Array.from(methodMap.entries()).map(([method, data]) => ({
    method,
    total_volume: data.volume,
    discrepancy_rate: (data.discrepancy / data.volume) * 100,
    discrepancy_amount: data.discrepancy,
  }));

  // Country analysis
  const countryMap = new Map<string, { volume: number; discrepancy: number }>();
  records.forEach(r => {
    const current = countryMap.get(r.country) || { volume: 0, discrepancy: 0 };
    countryMap.set(r.country, {
      volume: current.volume + r.amount,
      discrepancy: current.discrepancy + r.discrepancy_amount,
    });
  });

  const countryAnalysis = Array.from(countryMap.entries()).map(([country, data]) => ({
    country,
    total_volume: data.volume,
    discrepancy_rate: (data.discrepancy / data.volume) * 100,
    discrepancy_amount: data.discrepancy,
  }));

  return {
    summary: {
      total_transactions: records.length,
      total_transaction_amount: totalAmount,
      total_settled_amount: totalSettled,
      total_discrepancy_amount: totalDiscrepancy,
      discrepancy_percentage: (totalDiscrepancy / totalAmount) * 100,
    },
    category_breakdown: {
      unsettled_authorizations: { count: 50, amount: 15000 },
      missing_settlements: { count: anomalies.filter(a => a.anomaly_type === 'missing_settlement').length, amount: 250000 },
      unexpected_fees: { count: anomalies.filter(a => a.anomaly_type === 'fee_discrepancy').length, amount: 35000 },
      chargebacks: { count: records.filter(r => r.status === 'chargedback').length, amount: 12000 },
      refunds: { count: records.filter(r => r.status === 'refunded').length, amount: 28000 },
      timing_delays: { count: anomalies.filter(a => a.anomaly_type === 'timing_delay').length, amount: 45000 },
      ghost_settlements: { count: anomalies.filter(a => a.anomaly_type === 'ghost_settlement').length, amount: 8000 },
    },
    provider_analysis: providerAnalysis,
    method_analysis: methodAnalysis,
    country_analysis: countryAnalysis,
    top_patterns: [
      `${providerAnalysis[0]?.provider} has highest discrepancy rate at ${providerAnalysis[0]?.discrepancy_rate.toFixed(2)}%`,
      'Credit card settlements show 2-3 day delay pattern',
      `${countryAnalysis[0]?.country} accounts for ${((countryAnalysis[0]?.total_volume / totalAmount) * 100).toFixed(1)}% of total volume`,
    ],
  };
}

function generateTimeSeriesData(records: ReconciledRecord[]): TimeSeriesData[] {
  const dateMap = new Map<string, { volume: number; amount: number; settled: number }>();

  records.forEach(r => {
    const date = new Date(r.timestamp).toISOString().split('T')[0];
    const current = dateMap.get(date) || { volume: 0, amount: 0, settled: 0 };
    dateMap.set(date, {
      volume: current.volume + 1,
      amount: current.amount + r.amount,
      settled: current.settled + (r.actual_settled_amount || 0),
    });
  });

  return Array.from(dateMap.entries())
    .map(([date, data]) => ({
      date,
      transaction_volume: data.volume,
      transaction_amount: data.amount,
      settled_amount: data.settled,
    }))
    .sort((a, b) => a.date.localeCompare(b.date));
}

// Main data loading functions
export async function loadReconciledData(): Promise<ReconciledRecord[]> {
  try {
    // Try to load from actual data files
    const response = await fetch('/data/reconciled_data.json');
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.log('Using mock data - real data not available yet');
  }

  // Fall back to mock data
  return generateMockReconciledData();
}

export async function loadAnomalies(): Promise<Anomaly[]> {
  try {
    const response = await fetch('/data/anomalies.json');
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.log('Using mock anomalies - real data not available yet');
  }

  // Generate from mock reconciled data
  const records = generateMockReconciledData();
  return generateMockAnomalies(records);
}

export async function loadInsights(): Promise<Insight> {
  try {
    const response = await fetch('/data/insights.json');
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.log('Using mock insights - real data not available yet');
  }

  // Generate from mock data
  const records = generateMockReconciledData();
  const anomalies = generateMockAnomalies(records);
  return generateMockInsights(records, anomalies);
}

export async function loadTimeSeriesData(): Promise<TimeSeriesData[]> {
  const records = await loadReconciledData();
  return generateTimeSeriesData(records);
}

export async function loadAggregateMetrics(): Promise<AggregateMetrics> {
  const insights = await loadInsights();
  const records = await loadReconciledData();

  return {
    total_transaction_volume: insights.summary.total_transactions,
    total_transaction_amount: insights.summary.total_transaction_amount,
    total_settled_amount: insights.summary.total_settled_amount,
    total_discrepancy_amount: insights.summary.total_discrepancy_amount,
    discrepancy_percentage: insights.summary.discrepancy_percentage,
    unmatched_count: records.filter(r => r.settlement_status === 'missing').length,
    timing_anomalies_count: records.filter(r => r.timing_anomaly).length,
  };
}
