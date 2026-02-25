"""
Unit Tests for Analysis Module

This module tests revenue anomaly analysis functions including metrics calculation,
categorization, pattern identification, and insights generation.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add pipeline directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'pipeline'))

from analyze import (
    calculate_aggregate_metrics,
    categorize_revenue,
    identify_patterns,
    generate_prioritized_anomalies,
    generate_insights_summary
)


class TestCalculateAggregateMetrics:
    """Tests for aggregate metrics calculation."""

    def test_aggregate_metrics_basic_structure(self):
        """Test that aggregate metrics has correct structure."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'settlement_status': ['matched'],
            'actual_settled_amount': [96.80],
            'discrepancy_amount': [0.0],
            'provider': ['PayBridge'],
            'payment_method': ['credit_card'],
            'country': ['Brazil'],
            'timestamp': [pd.Timestamp('2026-02-01')]
        })

        metrics = calculate_aggregate_metrics(reconciled_df)

        assert 'overall' in metrics
        assert 'by_provider' in metrics
        assert 'by_payment_method' in metrics
        assert 'by_country' in metrics
        assert 'time_series' in metrics

    def test_aggregate_metrics_overall_calculations(self):
        """Test overall metrics calculations."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'amount': [100.0, 200.0],
            'currency': ['BRL', 'BRL'],
            'settlement_status': ['matched', 'missing'],
            'actual_settled_amount': [96.80, np.nan],
            'discrepancy_amount': [0.0, np.nan],
            'provider': ['PayBridge', 'PayBridge'],
            'payment_method': ['credit_card', 'credit_card'],
            'country': ['Brazil', 'Brazil'],
            'timestamp': [pd.Timestamp('2026-02-01'), pd.Timestamp('2026-02-01')]
        })

        metrics = calculate_aggregate_metrics(reconciled_df)

        assert metrics['overall']['total_transactions'] == 2
        assert metrics['overall']['total_amount_usd'] > 0
        assert metrics['overall']['missing_revenue_usd'] > 0

    def test_aggregate_metrics_provider_breakdown(self):
        """Test provider metrics breakdown."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002', 'TXN_003'],
            'amount': [100.0, 200.0, 300.0],
            'currency': ['BRL', 'BRL', 'BRL'],
            'settlement_status': ['matched', 'missing', 'matched'],
            'actual_settled_amount': [96.80, np.nan, 290.00],
            'discrepancy_amount': [0.0, np.nan, 0.0],
            'provider': ['PayBridge', 'PayBridge', 'LatamPay'],
            'payment_method': ['credit_card', 'credit_card', 'credit_card'],
            'country': ['Brazil', 'Brazil', 'Brazil'],
            'timestamp': [pd.Timestamp('2026-02-01')] * 3
        })

        metrics = calculate_aggregate_metrics(reconciled_df)

        assert len(metrics['by_provider']) == 2
        # Should be sorted by missing revenue
        assert metrics['by_provider'][0]['provider'] in ['PayBridge', 'LatamPay']

    def test_aggregate_metrics_payment_method_breakdown(self):
        """Test payment method metrics breakdown."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'amount': [100.0, 200.0],
            'currency': ['BRL', 'BRL'],
            'settlement_status': ['matched', 'matched'],
            'actual_settled_amount': [96.80, 197.00],
            'discrepancy_amount': [0.0, 0.0],
            'provider': ['PayBridge', 'PayBridge'],
            'payment_method': ['credit_card', 'bank_transfer'],
            'country': ['Brazil', 'Brazil'],
            'timestamp': [pd.Timestamp('2026-02-01')] * 2
        })

        metrics = calculate_aggregate_metrics(reconciled_df)

        assert len(metrics['by_payment_method']) == 2

    def test_aggregate_metrics_country_breakdown(self):
        """Test country metrics breakdown."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'amount': [100.0, 200.0],
            'currency': ['BRL', 'MXN'],
            'settlement_status': ['matched', 'matched'],
            'actual_settled_amount': [96.80, 197.00],
            'discrepancy_amount': [0.0, 0.0],
            'provider': ['PayBridge', 'LatamPay'],
            'payment_method': ['credit_card', 'credit_card'],
            'country': ['Brazil', 'Mexico'],
            'timestamp': [pd.Timestamp('2026-02-01')] * 2
        })

        metrics = calculate_aggregate_metrics(reconciled_df)

        assert len(metrics['by_country']) == 2

    def test_aggregate_metrics_time_series(self):
        """Test time series metrics."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002', 'TXN_003'],
            'amount': [100.0, 200.0, 300.0],
            'currency': ['BRL', 'BRL', 'BRL'],
            'settlement_status': ['matched', 'matched', 'missing'],
            'actual_settled_amount': [96.80, 197.00, np.nan],
            'discrepancy_amount': [0.0, 0.0, np.nan],
            'provider': ['PayBridge'] * 3,
            'payment_method': ['credit_card'] * 3,
            'country': ['Brazil'] * 3,
            'timestamp': [
                pd.Timestamp('2026-02-01'),
                pd.Timestamp('2026-02-02'),
                pd.Timestamp('2026-02-02')
            ]
        })

        metrics = calculate_aggregate_metrics(reconciled_df)

        assert len(metrics['time_series']) == 2  # Two distinct dates


class TestCategorizeRevenue:
    """Tests for revenue categorization."""

    def test_categorize_revenue_structure(self):
        """Test that categorization has correct structure."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'status': ['captured'],
            'settlement_status': ['matched'],
            'actual_settled_amount': [96.80],
            'discrepancy_amount': [0.0],
            'timing_anomaly': [False]
        })

        categories = categorize_revenue(reconciled_df)

        assert 'unsettled_authorizations' in categories
        assert 'missing_settlements' in categories
        assert 'unexpected_fees' in categories
        assert 'chargebacks' in categories
        assert 'refunds' in categories
        assert 'timing_delays' in categories
        assert 'ghost_settlements' in categories

    def test_categorize_unsettled_authorizations(self):
        """Test categorization of unsettled authorizations."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'amount': [100.0, 200.0],
            'currency': ['BRL', 'BRL'],
            'status': ['authorized', 'captured'],
            'settlement_status': ['not_applicable', 'matched'],
            'actual_settled_amount': [np.nan, 193.00],
            'discrepancy_amount': [np.nan, 0.0],
            'timing_anomaly': [False, False]
        })

        categories = categorize_revenue(reconciled_df)

        assert categories['unsettled_authorizations']['count'] == 1
        assert categories['unsettled_authorizations']['severity'] == 'low'

    def test_categorize_missing_settlements(self):
        """Test categorization of missing settlements."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'amount': [100.0, 200.0],
            'currency': ['BRL', 'BRL'],
            'status': ['captured', 'captured'],
            'settlement_status': ['missing', 'matched'],
            'actual_settled_amount': [np.nan, 193.00],
            'discrepancy_amount': [np.nan, 0.0],
            'timing_anomaly': [False, False]
        })

        categories = categorize_revenue(reconciled_df)

        assert categories['missing_settlements']['count'] == 1
        assert categories['missing_settlements']['severity'] == 'critical'
        assert categories['missing_settlements']['amount_usd'] > 0

    def test_categorize_unexpected_fees(self):
        """Test categorization of unexpected fees."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'status': ['captured'],
            'settlement_status': ['discrepancy'],
            'actual_settled_amount': [90.00],
            'discrepancy_amount': [5.0],
            'timing_anomaly': [False]
        })

        categories = categorize_revenue(reconciled_df)

        assert categories['unexpected_fees']['count'] == 1
        assert categories['unexpected_fees']['severity'] == 'high'

    def test_categorize_chargebacks(self):
        """Test categorization of chargebacks."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'status': ['chargedback'],
            'settlement_status': ['not_applicable'],
            'actual_settled_amount': [np.nan],
            'discrepancy_amount': [np.nan],
            'timing_anomaly': [False]
        })

        categories = categorize_revenue(reconciled_df)

        assert categories['chargebacks']['count'] == 1
        assert categories['chargebacks']['severity'] == 'medium'

    def test_categorize_refunds(self):
        """Test categorization of refunds."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'status': ['refunded'],
            'settlement_status': ['not_applicable'],
            'actual_settled_amount': [np.nan],
            'discrepancy_amount': [np.nan],
            'timing_anomaly': [False]
        })

        categories = categorize_revenue(reconciled_df)

        assert categories['refunds']['count'] == 1
        assert categories['refunds']['severity'] == 'low'

    def test_categorize_timing_delays(self):
        """Test categorization of timing delays."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'amount': [100.0, 200.0],
            'currency': ['BRL', 'BRL'],
            'status': ['captured', 'captured'],
            'settlement_status': ['matched', 'matched'],
            'actual_settled_amount': [96.80, 193.00],
            'discrepancy_amount': [0.0, 0.0],
            'timing_anomaly': [True, False]
        })

        categories = categorize_revenue(reconciled_df)

        assert categories['timing_delays']['count'] == 1
        assert categories['timing_delays']['severity'] == 'medium'


class TestIdentifyPatterns:
    """Tests for pattern identification."""

    def test_identify_patterns_returns_list(self):
        """Test that identify_patterns returns a list."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'status': ['captured'],
            'settlement_status': ['matched'],
            'provider': ['PayBridge'],
            'payment_method': ['credit_card'],
            'country': ['Brazil'],
            'timestamp': [pd.Timestamp('2026-02-01')],
            'timing_anomaly': [False]
        })

        categories = {
            'missing_settlements': {'count': 0, 'amount_usd': 0.0, 'severity': 'critical'}
        }

        patterns = identify_patterns(reconciled_df, categories)

        assert isinstance(patterns, list)

    def test_identify_patterns_provider_analysis(self):
        """Test that patterns include provider analysis."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002', 'TXN_003'],
            'amount': [100.0, 200.0, 300.0],
            'currency': ['BRL', 'BRL', 'BRL'],
            'status': ['captured', 'captured', 'captured'],
            'settlement_status': ['missing', 'missing', 'matched'],
            'provider': ['PayBridge', 'PayBridge', 'LatamPay'],
            'payment_method': ['credit_card'] * 3,
            'country': ['Brazil'] * 3,
            'timestamp': [pd.Timestamp('2026-02-01')] * 3,
            'timing_anomaly': [False] * 3
        })

        categories = {
            'missing_settlements': {'count': 2, 'amount_usd': 60.0, 'severity': 'critical'}
        }

        patterns = identify_patterns(reconciled_df, categories)

        # Should identify PayBridge as problematic provider
        assert any('PayBridge' in pattern for pattern in patterns)

    def test_identify_patterns_max_five(self):
        """Test that patterns are limited to top 5."""
        reconciled_df = pd.DataFrame({
            'transaction_id': [f'TXN_{i:03d}' for i in range(100)],
            'amount': [100.0] * 100,
            'currency': ['BRL'] * 100,
            'status': ['captured'] * 100,
            'settlement_status': ['matched'] * 100,
            'provider': ['PayBridge'] * 100,
            'payment_method': ['credit_card'] * 100,
            'country': ['Brazil'] * 100,
            'timestamp': [pd.Timestamp('2026-02-01')] * 100,
            'timing_anomaly': [False] * 100
        })

        categories = {
            'missing_settlements': {'count': 0, 'amount_usd': 0.0, 'severity': 'critical'}
        }

        patterns = identify_patterns(reconciled_df, categories)

        assert len(patterns) <= 5


class TestGeneratePrioritizedAnomalies:
    """Tests for prioritized anomaly generation."""

    def test_generate_anomalies_structure(self):
        """Test that anomalies have correct structure."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'status': ['captured'],
            'settlement_status': ['missing'],
            'provider': ['PayBridge'],
            'payment_method': ['credit_card'],
            'country': ['Brazil'],
            'timestamp': [pd.Timestamp('2026-02-01')],
            'timing_anomaly': [False]
        })

        anomalies = generate_prioritized_anomalies(reconciled_df)

        assert isinstance(anomalies, list)
        if len(anomalies) > 0:
            anomaly = anomalies[0]
            assert 'anomaly_id' in anomaly
            assert 'transaction_id' in anomaly
            assert 'provider' in anomaly
            assert 'anomaly_type' in anomaly
            assert 'severity' in anomaly
            assert 'suggested_action' in anomaly

    def test_generate_anomalies_missing_settlements(self):
        """Test anomaly generation for missing settlements."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'amount': [100.0, 200.0],
            'currency': ['BRL', 'BRL'],
            'status': ['captured', 'captured'],
            'settlement_status': ['missing', 'matched'],
            'provider': ['PayBridge', 'PayBridge'],
            'payment_method': ['credit_card', 'credit_card'],
            'country': ['Brazil', 'Brazil'],
            'timestamp': [pd.Timestamp('2026-02-01')] * 2,
            'timing_anomaly': [False, False],
            'actual_settled_amount': [np.nan, 193.00],
            'expected_settled_amount': [96.80, 193.00],
            'discrepancy_amount': [np.nan, 0.0]
        })

        anomalies = generate_prioritized_anomalies(reconciled_df)

        missing_anomalies = [a for a in anomalies if a['anomaly_type'] == 'missing_settlement']
        assert len(missing_anomalies) == 1
        assert missing_anomalies[0]['severity'] == 'critical'

    def test_generate_anomalies_fee_discrepancies(self):
        """Test anomaly generation for fee discrepancies."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'status': ['captured'],
            'settlement_status': ['discrepancy'],
            'provider': ['PayBridge'],
            'payment_method': ['credit_card'],
            'country': ['Brazil'],
            'timestamp': [pd.Timestamp('2026-02-01')],
            'timing_anomaly': [False],
            'actual_settled_amount': [90.00],
            'expected_settled_amount': [96.80],
            'discrepancy_amount': [6.80]
        })

        anomalies = generate_prioritized_anomalies(reconciled_df)

        fee_anomalies = [a for a in anomalies if a['anomaly_type'] == 'fee_discrepancy']
        assert len(fee_anomalies) == 1
        assert fee_anomalies[0]['severity'] == 'high'

    def test_generate_anomalies_timing_delays(self):
        """Test anomaly generation for timing delays."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'status': ['captured'],
            'settlement_status': ['matched'],
            'provider': ['PayBridge'],
            'payment_method': ['credit_card'],
            'country': ['Brazil'],
            'timestamp': [pd.Timestamp('2026-02-01')],
            'timing_anomaly': [True],
            'days_to_settle': [10],
            'actual_settled_amount': [96.80],
            'expected_settled_amount': [96.80]
        })

        anomalies = generate_prioritized_anomalies(reconciled_df)

        timing_anomalies = [a for a in anomalies if a['anomaly_type'] == 'timing_delay']
        assert len(timing_anomalies) == 1
        assert timing_anomalies[0]['severity'] == 'medium'

    def test_generate_anomalies_sorted_by_impact(self):
        """Test that anomalies are sorted by financial impact."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002', 'TXN_003'],
            'amount': [100.0, 500.0, 200.0],
            'currency': ['BRL', 'BRL', 'BRL'],
            'status': ['captured'] * 3,
            'settlement_status': ['missing'] * 3,
            'provider': ['PayBridge'] * 3,
            'payment_method': ['credit_card'] * 3,
            'country': ['Brazil'] * 3,
            'timestamp': [pd.Timestamp('2026-02-01')] * 3,
            'timing_anomaly': [False] * 3
        })

        anomalies = generate_prioritized_anomalies(reconciled_df)

        # Should be sorted by amount_usd (descending)
        amounts = [a['amount_usd'] for a in anomalies]
        assert amounts == sorted(amounts, reverse=True)

    def test_generate_anomalies_max_fifty(self):
        """Test that anomalies are limited to top 50."""
        reconciled_df = pd.DataFrame({
            'transaction_id': [f'TXN_{i:03d}' for i in range(100)],
            'amount': [100.0] * 100,
            'currency': ['BRL'] * 100,
            'status': ['captured'] * 100,
            'settlement_status': ['missing'] * 100,
            'provider': ['PayBridge'] * 100,
            'payment_method': ['credit_card'] * 100,
            'country': ['Brazil'] * 100,
            'timestamp': [pd.Timestamp('2026-02-01')] * 100,
            'timing_anomaly': [False] * 100
        })

        anomalies = generate_prioritized_anomalies(reconciled_df)

        assert len(anomalies) <= 50


class TestGenerateInsightsSummary:
    """Tests for insights summary generation."""

    def test_insights_summary_structure(self):
        """Test that insights summary has correct structure."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'provider': ['PayBridge'],
            'country': ['Brazil']
        })

        metrics = {
            'overall': {
                'total_transactions': 1,
                'total_amount_usd': 20.0,
                'total_settled_usd': 19.0,
                'missing_revenue_usd': 0.0,
                'discrepancy_amount_usd': 1.0,
                'total_discrepancy_usd': 1.0
            },
            'by_provider': [],
            'by_payment_method': [],
            'by_country': []
        }

        categories = {
            'missing_settlements': {'count': 0, 'amount_usd': 0.0, 'severity': 'critical'},
            'unexpected_fees': {'count': 0, 'amount_usd': 0.0, 'severity': 'high'},
            'timing_delays': {'count': 0, 'amount_usd': 0.0, 'severity': 'medium'},
            'unsettled_authorizations': {'count': 0, 'amount_usd': 0.0, 'severity': 'low'},
            'chargebacks': {'count': 0, 'amount_usd': 0.0, 'severity': 'medium'},
            'refunds': {'count': 0, 'amount_usd': 0.0, 'severity': 'low'},
            'ghost_settlements': {'count': 0, 'amount_usd': 0.0, 'severity': 'high'}
        }

        patterns = []

        insights = generate_insights_summary(metrics, categories, patterns, reconciled_df)

        assert 'generated_at' in insights
        assert 'summary' in insights
        assert 'category_breakdown' in insights
        assert 'top_root_causes' in insights
        assert 'recommendations' in insights

    def test_insights_summary_calculations(self):
        """Test that summary calculations are correct."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'provider': ['PayBridge'],
            'country': ['Brazil']
        })

        metrics = {
            'overall': {
                'total_transactions': 1,
                'total_amount_usd': 20.0,
                'total_settled_usd': 19.0,
                'missing_revenue_usd': 10.0,
                'discrepancy_amount_usd': 5.0,
                'total_discrepancy_usd': 15.0
            },
            'by_provider': [],
            'by_payment_method': [],
            'by_country': []
        }

        categories = {
            'missing_settlements': {'count': 1, 'amount_usd': 10.0, 'severity': 'critical'},
            'unexpected_fees': {'count': 1, 'amount_usd': 5.0, 'severity': 'high'},
            'timing_delays': {'count': 0, 'amount_usd': 0.0, 'severity': 'medium'},
            'unsettled_authorizations': {'count': 0, 'amount_usd': 0.0, 'severity': 'low'},
            'chargebacks': {'count': 0, 'amount_usd': 0.0, 'severity': 'medium'},
            'refunds': {'count': 0, 'amount_usd': 0.0, 'severity': 'low'},
            'ghost_settlements': {'count': 0, 'amount_usd': 0.0, 'severity': 'high'}
        }

        patterns = []

        insights = generate_insights_summary(metrics, categories, patterns, reconciled_df)

        assert insights['summary']['total_missing_revenue_usd'] == 15.0
        assert insights['summary']['total_transactions_analyzed'] == 1
        assert insights['summary']['critical_issues'] == 2

    def test_insights_has_recommendations(self):
        """Test that insights include recommendations."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'provider': ['PayBridge'],
            'country': ['Brazil']
        })

        metrics = {
            'overall': {'total_transactions': 1},
            'by_provider': [],
            'by_payment_method': [],
            'by_country': []
        }

        categories = {
            'missing_settlements': {'count': 0, 'amount_usd': 0.0, 'severity': 'critical'},
            'unexpected_fees': {'count': 0, 'amount_usd': 0.0, 'severity': 'high'},
            'timing_delays': {'count': 0, 'amount_usd': 0.0, 'severity': 'medium'},
            'unsettled_authorizations': {'count': 0, 'amount_usd': 0.0, 'severity': 'low'},
            'chargebacks': {'count': 0, 'amount_usd': 0.0, 'severity': 'medium'},
            'refunds': {'count': 0, 'amount_usd': 0.0, 'severity': 'low'},
            'ghost_settlements': {'count': 0, 'amount_usd': 0.0, 'severity': 'high'}
        }

        patterns = []

        insights = generate_insights_summary(metrics, categories, patterns, reconciled_df)

        assert isinstance(insights['recommendations'], list)
        assert len(insights['recommendations']) > 0


class TestEdgeCases:
    """Tests for edge cases in analysis functions."""

    def test_empty_dataframe(self):
        """Test handling of empty dataframes."""
        empty_df = pd.DataFrame()

        # Should not crash
        anomalies = generate_prioritized_anomalies(empty_df)
        assert len(anomalies) == 0

    def test_single_transaction_analysis(self):
        """Test analysis with single transaction."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'currency': ['BRL'],
            'status': ['captured'],
            'settlement_status': ['matched'],
            'provider': ['PayBridge'],
            'payment_method': ['credit_card'],
            'country': ['Brazil'],
            'timestamp': [pd.Timestamp('2026-02-01')],
            'timing_anomaly': [False],
            'actual_settled_amount': [96.80],
            'discrepancy_amount': [0.0]
        })

        metrics = calculate_aggregate_metrics(reconciled_df)
        assert metrics['overall']['total_transactions'] == 1

    def test_all_currencies_handled(self):
        """Test that all supported currencies are handled."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002', 'TXN_003', 'TXN_004'],
            'amount': [100.0, 100.0, 100.0, 100.0],
            'currency': ['BRL', 'MXN', 'COP', 'CLP'],
            'status': ['captured'] * 4,
            'settlement_status': ['matched'] * 4,
            'provider': ['PayBridge'] * 4,
            'payment_method': ['credit_card'] * 4,
            'country': ['Brazil', 'Mexico', 'Colombia', 'Chile'],
            'timestamp': [pd.Timestamp('2026-02-01')] * 4,
            'timing_anomaly': [False] * 4,
            'actual_settled_amount': [96.80] * 4,
            'discrepancy_amount': [0.0] * 4
        })

        metrics = calculate_aggregate_metrics(reconciled_df)
        # Should calculate USD amounts for all currencies
        assert metrics['overall']['total_amount_usd'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
