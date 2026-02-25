"""
Unit Tests for Reconciliation Module

This module tests the core reconciliation logic including settlement matching,
discrepancy detection, timing anomaly identification, and status classification.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add pipeline directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'pipeline'))

from reconcile import (
    load_data,
    calculate_expected_amounts,
    match_settlements_exact,
    calculate_discrepancies,
    detect_timing_anomalies,
    classify_settlement_status,
    identify_ghost_settlements,
    calculate_expected_settlement_date,
    reconcile_transactions
)


class TestLoadData:
    """Tests for data loading functionality."""

    @patch('reconcile.pd.read_csv')
    def test_load_data_success(self, mock_read_csv):
        """Test successful data loading."""
        # Create mock dataframes
        txn_data = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'timestamp': ['2026-02-01 10:00:00'],
            'amount': [100.0]
        })
        settle_data = pd.DataFrame({
            'settlement_id': ['SET_001'],
            'transaction_id': ['TXN_001'],
            'settlement_date': ['2026-02-03 10:00:00']
        })

        mock_read_csv.side_effect = [txn_data, settle_data]

        transactions_df, settlements_df = load_data()

        assert len(transactions_df) == 1
        assert len(settlements_df) == 1
        assert 'transaction_id' in transactions_df.columns
        assert 'settlement_id' in settlements_df.columns

    @patch('reconcile.pd.read_csv')
    def test_load_data_converts_timestamps(self, mock_read_csv):
        """Test that timestamps are converted to datetime objects."""
        txn_data = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'timestamp': ['2026-02-01 10:00:00'],
            'amount': [100.0]
        })
        settle_data = pd.DataFrame({
            'settlement_id': ['SET_001'],
            'transaction_id': ['TXN_001'],
            'settlement_date': ['2026-02-03 10:00:00']
        })

        mock_read_csv.side_effect = [txn_data, settle_data]

        transactions_df, settlements_df = load_data()

        assert pd.api.types.is_datetime64_any_dtype(transactions_df['timestamp'])
        assert pd.api.types.is_datetime64_any_dtype(settlements_df['settlement_date'])

    @patch('reconcile.pd.read_csv')
    def test_load_data_file_not_found(self, mock_read_csv):
        """Test handling of missing data files."""
        mock_read_csv.side_effect = FileNotFoundError("File not found")

        with pytest.raises(FileNotFoundError):
            load_data()


class TestCalculateExpectedAmounts:
    """Tests for expected settlement amount calculation."""

    def test_calculate_expected_amounts_adds_column(self):
        """Test that function adds expected_settled_amount column."""
        transactions_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'amount': [100.0, 200.0],
            'payment_method': ['credit_card', 'bank_transfer']
        })

        result_df = calculate_expected_amounts(transactions_df)

        assert 'expected_settled_amount' in result_df.columns
        assert len(result_df) == 2

    def test_calculate_expected_amounts_credit_card(self):
        """Test expected amount calculation for credit card."""
        transactions_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'payment_method': ['credit_card']
        })

        result_df = calculate_expected_amounts(transactions_df)

        # 100 - (100 * 0.029 + 0.30) = 96.80
        assert result_df['expected_settled_amount'].iloc[0] == pytest.approx(96.80, rel=1e-2)

    def test_calculate_expected_amounts_bank_transfer(self):
        """Test expected amount calculation for bank transfer."""
        transactions_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [1000.0],
            'payment_method': ['bank_transfer']
        })

        result_df = calculate_expected_amounts(transactions_df)

        # 1000 - (1000 * 0.015) = 985.00
        assert result_df['expected_settled_amount'].iloc[0] == 985.00

    def test_calculate_expected_amounts_preserves_original(self):
        """Test that original dataframe is not modified."""
        transactions_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'payment_method': ['credit_card']
        })

        original_columns = transactions_df.columns.tolist()
        result_df = calculate_expected_amounts(transactions_df)

        # Original should not have new column
        assert 'expected_settled_amount' not in transactions_df.columns
        # Result should have new column
        assert 'expected_settled_amount' in result_df.columns


class TestMatchSettlementsExact:
    """Tests for exact settlement matching."""

    def test_match_settlements_exact_success(self):
        """Test successful exact matching of settlements."""
        transactions_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'amount': [100.0, 200.0],
            'provider': ['PayBridge', 'LatamPay']
        })

        settlements_df = pd.DataFrame({
            'settlement_id': ['SET_001'],
            'transaction_id': ['TXN_001'],
            'settled_amount': [96.80],
            'provider': ['PayBridge']
        })

        result_df = match_settlements_exact(transactions_df, settlements_df)

        assert len(result_df) == 2
        assert 'settlement_id' in result_df.columns
        assert result_df[result_df['transaction_id'] == 'TXN_001']['settlement_id'].iloc[0] == 'SET_001'
        assert pd.isna(result_df[result_df['transaction_id'] == 'TXN_002']['settlement_id'].iloc[0])

    def test_match_settlements_left_join(self):
        """Test that matching uses left join (keeps all transactions)."""
        transactions_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002', 'TXN_003'],
            'amount': [100.0, 200.0, 300.0]
        })

        settlements_df = pd.DataFrame({
            'settlement_id': ['SET_001'],
            'transaction_id': ['TXN_001'],
            'settled_amount': [96.80]
        })

        result_df = match_settlements_exact(transactions_df, settlements_df)

        # Should keep all 3 transactions
        assert len(result_df) == 3

    def test_match_settlements_removes_duplicate_columns(self):
        """Test that duplicate provider/currency columns are removed."""
        transactions_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'amount': [100.0],
            'provider': ['PayBridge'],
            'currency': ['BRL']
        })

        settlements_df = pd.DataFrame({
            'settlement_id': ['SET_001'],
            'transaction_id': ['TXN_001'],
            'settled_amount': [96.80],
            'provider': ['PayBridge'],
            'currency': ['BRL']
        })

        result_df = match_settlements_exact(transactions_df, settlements_df)

        # Should not have _settlement suffix columns
        assert 'provider_settlement' not in result_df.columns
        assert 'currency_settlement' not in result_df.columns


class TestCalculateDiscrepancies:
    """Tests for discrepancy calculation."""

    def test_calculate_discrepancies_adds_columns(self):
        """Test that function adds required columns."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'expected_settled_amount': [96.80],
            'settled_amount': [96.80]
        })

        result_df = calculate_discrepancies(reconciled_df)

        assert 'actual_settled_amount' in result_df.columns
        assert 'discrepancy_amount' in result_df.columns
        assert 'discrepancy_percent' in result_df.columns

    def test_calculate_discrepancies_no_discrepancy(self):
        """Test discrepancy calculation when amounts match."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'expected_settled_amount': [96.80],
            'settled_amount': [96.80]
        })

        result_df = calculate_discrepancies(reconciled_df)

        assert result_df['discrepancy_amount'].iloc[0] == 0.0
        assert result_df['discrepancy_percent'].iloc[0] == 0.0

    def test_calculate_discrepancies_with_discrepancy(self):
        """Test discrepancy calculation when amounts differ."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'expected_settled_amount': [100.0],
            'settled_amount': [95.0]
        })

        result_df = calculate_discrepancies(reconciled_df)

        assert result_df['discrepancy_amount'].iloc[0] == 5.0
        assert result_df['discrepancy_percent'].iloc[0] == pytest.approx(5.0, rel=1e-2)

    def test_calculate_discrepancies_no_settlement(self):
        """Test discrepancy calculation when no settlement exists."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'expected_settled_amount': [96.80],
            'settled_amount': [np.nan]
        })

        result_df = calculate_discrepancies(reconciled_df)

        assert pd.isna(result_df['discrepancy_amount'].iloc[0])
        assert pd.isna(result_df['discrepancy_percent'].iloc[0])


class TestDetectTimingAnomalies:
    """Tests for timing anomaly detection."""

    def test_detect_timing_anomalies_adds_columns(self):
        """Test that function adds required columns."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'timestamp': [pd.Timestamp('2026-02-01 10:00:00')],
            'settlement_date': [pd.Timestamp('2026-02-03 10:00:00')],
            'payment_method': ['credit_card']
        })

        result_df = detect_timing_anomalies(reconciled_df)

        assert 'days_to_settle' in result_df.columns
        assert 'timing_anomaly' in result_df.columns

    def test_detect_timing_anomalies_normal_card(self):
        """Test timing detection for normal card settlement."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'timestamp': [pd.Timestamp('2026-02-01 10:00:00')],
            'settlement_date': [pd.Timestamp('2026-02-03 10:00:00')],
            'payment_method': ['credit_card']
        })

        result_df = detect_timing_anomalies(reconciled_df)

        assert result_df['days_to_settle'].iloc[0] == 2
        assert result_df['timing_anomaly'].iloc[0] == False

    def test_detect_timing_anomalies_delayed_card(self):
        """Test timing detection for delayed card settlement."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'timestamp': [pd.Timestamp('2026-02-01 10:00:00')],
            'settlement_date': [pd.Timestamp('2026-02-08 10:00:00')],  # 7 days
            'payment_method': ['credit_card']
        })

        result_df = detect_timing_anomalies(reconciled_df)

        assert result_df['days_to_settle'].iloc[0] == 7
        # Threshold is 5 days for cards
        assert result_df['timing_anomaly'].iloc[0] == True

    def test_detect_timing_anomalies_no_settlement(self):
        """Test timing detection when no settlement exists."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'timestamp': [pd.Timestamp('2026-02-01 10:00:00')],
            'settlement_date': [pd.NaT],
            'payment_method': ['credit_card']
        })

        result_df = detect_timing_anomalies(reconciled_df)

        assert pd.isna(result_df['days_to_settle'].iloc[0])
        assert result_df['timing_anomaly'].iloc[0] == False


class TestClassifySettlementStatus:
    """Tests for settlement status classification."""

    def test_classify_matched_settlement(self):
        """Test classification of matched settlement."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'status': ['captured'],
            'settlement_id': ['SET_001'],
            'discrepancy_amount': [0.0],
            'discrepancy_percent': [0.0]
        })

        result_df = classify_settlement_status(reconciled_df)

        assert result_df['settlement_status'].iloc[0] == 'matched'

    def test_classify_missing_settlement(self):
        """Test classification of missing settlement."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'status': ['captured'],
            'settlement_id': [np.nan]
        })

        result_df = classify_settlement_status(reconciled_df)

        assert result_df['settlement_status'].iloc[0] == 'missing'

    def test_classify_authorized_not_applicable(self):
        """Test classification of authorized-only transaction."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'status': ['authorized'],
            'settlement_id': [np.nan]
        })

        result_df = classify_settlement_status(reconciled_df)

        assert result_df['settlement_status'].iloc[0] == 'not_applicable'

    def test_classify_declined_not_applicable(self):
        """Test classification of declined transaction."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'status': ['declined'],
            'settlement_id': [np.nan]
        })

        result_df = classify_settlement_status(reconciled_df)

        assert result_df['settlement_status'].iloc[0] == 'not_applicable'

    def test_classify_discrepancy(self):
        """Test classification of settlement with discrepancy."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'status': ['captured'],
            'settlement_id': ['SET_001'],
            'discrepancy_amount': [5.0],
            'discrepancy_percent': [5.0]
        })

        result_df = classify_settlement_status(reconciled_df)

        assert result_df['settlement_status'].iloc[0] == 'discrepancy'

    def test_classify_refunded_missing_expected(self):
        """Test classification of refunded transaction."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'status': ['refunded'],
            'settlement_id': [np.nan]
        })

        result_df = classify_settlement_status(reconciled_df)

        assert result_df['settlement_status'].iloc[0] == 'missing_expected'


class TestIdentifyGhostSettlements:
    """Tests for ghost settlement identification."""

    def test_identify_ghost_settlements_found(self):
        """Test identification of ghost settlements."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'settlement_id': ['SET_001']
        })

        settlements_df = pd.DataFrame({
            'settlement_id': ['SET_001', 'SET_999'],
            'transaction_id': ['TXN_001', 'TXN_999'],
            'settled_amount': [96.80, 100.0]
        })

        ghost_df = identify_ghost_settlements(reconciled_df, settlements_df)

        assert len(ghost_df) == 1
        assert ghost_df['settlement_id'].iloc[0] == 'SET_999'
        assert ghost_df['anomaly_type'].iloc[0] == 'ghost_settlement'

    def test_identify_ghost_settlements_none_found(self):
        """Test when no ghost settlements exist."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'settlement_id': ['SET_001', 'SET_002']
        })

        settlements_df = pd.DataFrame({
            'settlement_id': ['SET_001', 'SET_002'],
            'transaction_id': ['TXN_001', 'TXN_002'],
            'settled_amount': [96.80, 96.80]
        })

        ghost_df = identify_ghost_settlements(reconciled_df, settlements_df)

        assert len(ghost_df) == 0

    def test_identify_ghost_settlements_with_nulls(self):
        """Test ghost settlement identification with null settlement IDs."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'settlement_id': ['SET_001', np.nan]
        })

        settlements_df = pd.DataFrame({
            'settlement_id': ['SET_001', 'SET_999'],
            'transaction_id': ['TXN_001', 'TXN_999'],
            'settled_amount': [96.80, 100.0]
        })

        ghost_df = identify_ghost_settlements(reconciled_df, settlements_df)

        assert len(ghost_df) == 1
        assert ghost_df['settlement_id'].iloc[0] == 'SET_999'


class TestCalculateExpectedSettlementDate:
    """Tests for expected settlement date calculation."""

    def test_expected_date_credit_card(self):
        """Test expected settlement date for credit card."""
        row = pd.Series({
            'timestamp': pd.Timestamp('2026-02-01 10:00:00'),
            'payment_method': 'credit_card'
        })

        expected_date = calculate_expected_settlement_date(row)

        # Card: min 2, max 3, avg 2.5 days
        assert expected_date == pd.Timestamp('2026-02-03 22:00:00')

    def test_expected_date_bank_transfer(self):
        """Test expected settlement date for bank transfer."""
        row = pd.Series({
            'timestamp': pd.Timestamp('2026-02-01 10:00:00'),
            'payment_method': 'bank_transfer'
        })

        expected_date = calculate_expected_settlement_date(row)

        # Bank: min 5, max 7, avg 6 days
        assert expected_date == pd.Timestamp('2026-02-07 10:00:00')

    def test_expected_date_cash_voucher(self):
        """Test expected settlement date for cash voucher."""
        row = pd.Series({
            'timestamp': pd.Timestamp('2026-02-01 10:00:00'),
            'payment_method': 'cash_voucher'
        })

        expected_date = calculate_expected_settlement_date(row)

        # Voucher: min 3, max 5, avg 4 days
        assert expected_date == pd.Timestamp('2026-02-05 10:00:00')


class TestReconcileTransactionsIntegration:
    """Integration tests for the full reconciliation process."""

    @patch('reconcile.load_data')
    def test_reconcile_transactions_full_flow(self, mock_load_data):
        """Test full reconciliation flow with mock data."""
        # Create mock data
        transactions_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'timestamp': [pd.Timestamp('2026-02-01'), pd.Timestamp('2026-02-01')],
            'amount': [100.0, 200.0],
            'currency': ['BRL', 'MXN'],
            'status': ['captured', 'captured'],
            'provider': ['PayBridge', 'LatamPay'],
            'payment_method': ['credit_card', 'bank_transfer'],
            'country': ['Brazil', 'Mexico']
        })

        settlements_df = pd.DataFrame({
            'settlement_id': ['SET_001'],
            'transaction_id': ['TXN_001'],
            'settlement_date': [pd.Timestamp('2026-02-03')],
            'settled_amount': [96.80],
            'currency': ['BRL'],
            'provider': ['PayBridge']
        })

        mock_load_data.return_value = (transactions_df, settlements_df)

        reconciled_df, ghost_df = reconcile_transactions()

        # Check reconciled data
        assert len(reconciled_df) == 2
        assert 'settlement_status' in reconciled_df.columns
        assert 'expected_settled_amount' in reconciled_df.columns
        assert 'timing_anomaly' in reconciled_df.columns

        # Check settlement statuses
        assert reconciled_df[reconciled_df['transaction_id'] == 'TXN_001']['settlement_status'].iloc[0] == 'matched'
        assert reconciled_df[reconciled_df['transaction_id'] == 'TXN_002']['settlement_status'].iloc[0] == 'missing'


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_dataframe(self):
        """Test handling of empty dataframes."""
        empty_df = pd.DataFrame()

        # Should not crash
        result_df = calculate_discrepancies(empty_df)
        assert len(result_df) == 0

    def test_single_transaction(self):
        """Test handling of single transaction."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001'],
            'status': ['captured'],
            'settlement_id': [np.nan]
        })

        result_df = classify_settlement_status(reconciled_df)

        assert len(result_df) == 1
        assert result_df['settlement_status'].iloc[0] == 'missing'

    def test_all_matched(self):
        """Test when all transactions are matched."""
        reconciled_df = pd.DataFrame({
            'transaction_id': ['TXN_001', 'TXN_002'],
            'settlement_id': ['SET_001', 'SET_002']
        })

        settlements_df = pd.DataFrame({
            'settlement_id': ['SET_001', 'SET_002'],
            'transaction_id': ['TXN_001', 'TXN_002']
        })

        ghost_df = identify_ghost_settlements(reconciled_df, settlements_df)

        assert len(ghost_df) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
