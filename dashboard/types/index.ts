// Transaction data types based on the solution plan schemas

export interface Transaction {
  transaction_id: string;
  timestamp: string;
  amount: number;
  currency: string;
  status: 'approved' | 'captured' | 'declined' | 'pending' | 'refunded' | 'chargedback';
  provider: string;
  payment_method: 'credit_card' | 'debit_card' | 'bank_transfer' | 'cash_voucher';
  country: string;
  customer_id: string;
}

export interface Settlement {
  settlement_id: string;
  transaction_id: string;
  settlement_date: string;
  settled_amount: number;
  currency: string;
  provider: string;
}

export interface ReconciledRecord extends Transaction {
  settlement_id: string | null;
  settlement_date: string | null;
  expected_settled_amount: number;
  actual_settled_amount: number | null;
  settlement_status: 'matched' | 'missing' | 'discrepancy' | 'ghost';
  timing_anomaly: boolean;
  discrepancy_amount: number;
  days_to_settle: number | null;
}

export interface Anomaly {
  anomaly_id: string;
  transaction_id: string;
  date: string;
  provider: string;
  payment_method: string;
  country: string;
  anomaly_type: 'missing_settlement' | 'fee_discrepancy' | 'timing_delay' | 'ghost_settlement';
  category: string;
  amount: number;
  currency: string;
  amount_usd: number;
  expected_amount?: number;
  actual_amount?: number;
  discrepancy?: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  suggested_action: string;
}

export interface CategoryBreakdown {
  count: number;
  amount: number;
}

export interface ProviderAnalysis {
  provider: string;
  total_volume: number;
  discrepancy_rate: number;
  discrepancy_amount: number;
}

export interface Insight {
  summary: {
    total_transactions: number;
    total_transaction_amount: number;
    total_settled_amount: number;
    total_discrepancy_amount: number;
    discrepancy_percentage: number;
  };
  category_breakdown: {
    unsettled_authorizations: CategoryBreakdown;
    missing_settlements: CategoryBreakdown;
    unexpected_fees: CategoryBreakdown;
    chargebacks: CategoryBreakdown;
    refunds: CategoryBreakdown;
    timing_delays: CategoryBreakdown;
    ghost_settlements: CategoryBreakdown;
  };
  provider_analysis: ProviderAnalysis[];
  method_analysis: Array<{
    method: string;
    total_volume: number;
    discrepancy_rate: number;
    discrepancy_amount: number;
  }>;
  country_analysis: Array<{
    country: string;
    total_volume: number;
    discrepancy_rate: number;
    discrepancy_amount: number;
  }>;
  top_patterns: string[];
}

export interface AggregateMetrics {
  total_transaction_volume: number;
  total_transaction_amount: number;
  total_settled_amount: number;
  total_discrepancy_amount: number;
  discrepancy_percentage: number;
  unmatched_count: number;
  timing_anomalies_count: number;
}

export interface FilterState {
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
  providers: string[];
  countries: string[];
  paymentMethods: string[];
}

export interface TimeSeriesData {
  date: string;
  transaction_volume: number;
  transaction_amount: number;
  settled_amount: number;
}
