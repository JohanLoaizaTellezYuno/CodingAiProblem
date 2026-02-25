'use client';

import { useState, useEffect } from 'react';
import MetricsOverview from '@/components/MetricsOverview';
import TimeSeriesChart from '@/components/TimeSeriesChart';
import BreakdownCharts from '@/components/BreakdownCharts';
import AnomalyFeed from '@/components/AnomalyFeed';
import Filters from '@/components/Filters';
import {
  loadReconciledData,
  loadAnomalies,
  loadInsights,
  loadTimeSeriesData,
  loadAggregateMetrics,
} from '@/lib/data';
import {
  ReconciledRecord,
  Anomaly,
  Insight,
  TimeSeriesData,
  AggregateMetrics,
  FilterState,
} from '@/types';

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<ReconciledRecord[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [insights, setInsights] = useState<Insight | null>(null);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([]);
  const [metrics, setMetrics] = useState<AggregateMetrics | null>(null);

  const [filters, setFilters] = useState<FilterState>({
    dateRange: { start: null, end: null },
    providers: [],
    countries: [],
    paymentMethods: [],
  });

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [reconciledData, anomaliesData, insightsData, tsData, metricsData] = await Promise.all([
          loadReconciledData(),
          loadAnomalies(),
          loadInsights(),
          loadTimeSeriesData(),
          loadAggregateMetrics(),
        ]);

        setData(reconciledData);
        setAnomalies(anomaliesData);
        setInsights(insightsData);
        setTimeSeriesData(tsData);
        setMetrics(metricsData);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  // Apply filters to data
  const filteredData = data.filter(record => {
    if (filters.dateRange.start && new Date(record.timestamp) < filters.dateRange.start) {
      return false;
    }
    if (filters.dateRange.end && new Date(record.timestamp) > filters.dateRange.end) {
      return false;
    }
    if (filters.providers.length > 0 && !filters.providers.includes(record.provider)) {
      return false;
    }
    if (filters.countries.length > 0 && !filters.countries.includes(record.country)) {
      return false;
    }
    if (filters.paymentMethods.length > 0 && !filters.paymentMethods.includes(record.payment_method)) {
      return false;
    }
    return true;
  });

  const filteredAnomalies = anomalies.filter(anomaly => {
    if (filters.dateRange.start && new Date(anomaly.date) < filters.dateRange.start) {
      return false;
    }
    if (filters.dateRange.end && new Date(anomaly.date) > filters.dateRange.end) {
      return false;
    }
    if (filters.providers.length > 0 && !filters.providers.includes(anomaly.provider)) {
      return false;
    }
    if (filters.countries.length > 0 && !filters.countries.includes(anomaly.country)) {
      return false;
    }
    if (filters.paymentMethods.length > 0 && !filters.paymentMethods.includes(anomaly.payment_method)) {
      return false;
    }
    return true;
  });

  // Recalculate metrics based on filtered data
  const filteredMetrics: AggregateMetrics = metrics
    ? {
        total_transaction_volume: filteredData.length,
        total_transaction_amount: filteredData.reduce((sum, r) => sum + r.amount, 0),
        total_settled_amount: filteredData.reduce((sum, r) => sum + (r.actual_settled_amount || 0), 0),
        total_discrepancy_amount: filteredData.reduce((sum, r) => sum + r.discrepancy_amount, 0),
        discrepancy_percentage:
          filteredData.length > 0
            ? (filteredData.reduce((sum, r) => sum + r.discrepancy_amount, 0) /
                filteredData.reduce((sum, r) => sum + r.amount, 0)) *
              100
            : 0,
        unmatched_count: filteredData.filter(r => r.settlement_status === 'missing').length,
        timing_anomalies_count: filteredData.filter(r => r.timing_anomaly).length,
      }
    : metrics!;

  // Get unique values for filter options
  const availableProviders = [...new Set(data.map(r => r.provider))];
  const availableCountries = [...new Set(data.map(r => r.country))];
  const availablePaymentMethods = [...new Set(data.map(r => r.payment_method))];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600 font-medium">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Horizon Gaming</h1>
              <p className="text-blue-100 mt-1">Revenue Anomaly Detector</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-blue-100">Real-time Reconciliation</p>
              <p className="text-xs text-blue-200 mt-1">
                Last updated: {new Date().toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <Filters
          filters={filters}
          onChange={setFilters}
          availableProviders={availableProviders}
          availableCountries={availableCountries}
          availablePaymentMethods={availablePaymentMethods}
        />

        {/* Metrics Overview */}
        {filteredMetrics && <MetricsOverview metrics={filteredMetrics} />}

        {/* Time Series Chart */}
        <TimeSeriesChart data={timeSeriesData} />

        {/* Breakdown Charts */}
        {insights && <BreakdownCharts insights={insights} />}

        {/* Anomaly Feed */}
        <AnomalyFeed anomalies={filteredAnomalies} />

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-gray-500 pb-8">
          <p>Horizon Gaming Revenue Anomaly Detector v1.0</p>
          <p className="mt-1">
            Monitoring {data.length} transactions across {availableProviders.length} providers in{' '}
            {availableCountries.length} countries
          </p>
        </footer>
      </main>
    </div>
  );
}
