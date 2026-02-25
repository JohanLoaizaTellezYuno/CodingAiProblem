"""
Integration Tests for Full Pipeline

This module tests the complete end-to-end pipeline execution including
data generation, reconciliation, analysis, and output file generation.
"""

import pytest
import pandas as pd
import json
import sys
from pathlib import Path
from unittest.mock import patch
import shutil
import os

# Add pipeline directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'pipeline'))

from config import Config


@pytest.fixture(scope="module")
def test_data_paths(tmp_path_factory):
    """Set up temporary paths for test execution (module-scoped)."""
    # Create temporary directories using module-scoped tmp_path_factory
    tmp_path = tmp_path_factory.mktemp("test_data")
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    # Copy test fixtures to temporary raw directory
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    shutil.copy(
        fixtures_dir / "test_transactions.csv",
        raw_dir / "transactions.csv"
    )
    shutil.copy(
        fixtures_dir / "test_settlements.csv",
        raw_dir / "settlements.csv"
    )

    # Store original config paths
    original_txn_path = Config.TRANSACTIONS_DATA_PATH
    original_settle_path = Config.SETTLEMENTS_DATA_PATH
    original_output_path = Config.OUTPUT_PATH

    # Set temporary paths
    Config.TRANSACTIONS_DATA_PATH = str(raw_dir / "transactions.csv")
    Config.SETTLEMENTS_DATA_PATH = str(raw_dir / "settlements.csv")
    Config.OUTPUT_PATH = str(processed_dir) + "/"

    yield {
        'raw_dir': raw_dir,
        'processed_dir': processed_dir,
        'transactions_path': Config.TRANSACTIONS_DATA_PATH,
        'settlements_path': Config.SETTLEMENTS_DATA_PATH,
        'output_path': Config.OUTPUT_PATH
    }

    # Restore original paths
    Config.TRANSACTIONS_DATA_PATH = original_txn_path
    Config.SETTLEMENTS_DATA_PATH = original_settle_path
    Config.OUTPUT_PATH = original_output_path


class TestFullPipelineExecution:
    """Integration tests for complete pipeline execution."""

    def test_reconciliation_pipeline_execution(self, test_data_paths):
        """Test that reconciliation pipeline executes successfully."""
        from reconcile import reconcile_transactions, save_reconciled_data

        # Execute reconciliation
        reconciled_df, ghost_settlements = reconcile_transactions()

        # Verify outputs exist
        assert reconciled_df is not None
        assert ghost_settlements is not None

        # Verify data structure
        assert len(reconciled_df) > 0
        assert 'settlement_status' in reconciled_df.columns
        assert 'expected_settled_amount' in reconciled_df.columns
        assert 'timing_anomaly' in reconciled_df.columns

        # Save outputs
        save_reconciled_data(reconciled_df, ghost_settlements)

        # Verify files were created
        reconciled_path = Path(test_data_paths['output_path']) / "reconciled_data.csv"
        ghost_path = Path(test_data_paths['output_path']) / "ghost_settlements.csv"

        assert reconciled_path.exists()
        assert ghost_path.exists()

    def test_analysis_pipeline_execution(self, test_data_paths):
        """Test that analysis pipeline executes successfully."""
        from reconcile import reconcile_transactions, save_reconciled_data
        from analyze import analyze_revenue_anomalies

        # First run reconciliation
        reconciled_df, ghost_settlements = reconcile_transactions()
        save_reconciled_data(reconciled_df, ghost_settlements)

        # Then run analysis
        insights, anomalies = analyze_revenue_anomalies()

        # Verify outputs exist
        assert insights is not None
        assert anomalies is not None

        # Verify insights structure
        assert 'summary' in insights
        assert 'category_breakdown' in insights
        assert 'recommendations' in insights

        # Verify anomalies structure
        assert isinstance(anomalies, list)

        # Verify files were created
        insights_path = Path(test_data_paths['output_path']) / "insights.json"
        anomalies_path = Path(test_data_paths['output_path']) / "anomalies.json"

        assert insights_path.exists()
        assert anomalies_path.exists()

    def test_output_file_generation(self, test_data_paths):
        """Test that all expected output files are generated."""
        from reconcile import reconcile_transactions, save_reconciled_data
        from analyze import analyze_revenue_anomalies

        # Run full pipeline
        reconciled_df, ghost_settlements = reconcile_transactions()
        save_reconciled_data(reconciled_df, ghost_settlements)
        insights, anomalies = analyze_revenue_anomalies()

        output_dir = Path(test_data_paths['output_path'])

        # Check all expected files exist
        expected_files = [
            'reconciled_data.csv',
            'ghost_settlements.csv',
            'insights.json',
            'anomalies.json'
        ]

        for file_name in expected_files:
            file_path = output_dir / file_name
            assert file_path.exists(), f"Expected file {file_name} not found"

    def test_reconciled_data_structure(self, test_data_paths):
        """Test that reconciled data has correct structure."""
        from reconcile import reconcile_transactions, save_reconciled_data

        reconciled_df, ghost_settlements = reconcile_transactions()
        save_reconciled_data(reconciled_df, ghost_settlements)

        # Load the saved file
        reconciled_path = Path(test_data_paths['output_path']) / "reconciled_data.csv"
        df = pd.read_csv(reconciled_path)

        # Verify required columns exist
        required_columns = [
            'transaction_id',
            'timestamp',
            'amount',
            'currency',
            'status',
            'provider',
            'payment_method',
            'country',
            'expected_settled_amount',
            'settlement_status',
            'timing_anomaly'
        ]

        for col in required_columns:
            assert col in df.columns, f"Required column {col} missing from reconciled data"

    def test_insights_json_structure(self, test_data_paths):
        """Test that insights JSON has correct structure."""
        from reconcile import reconcile_transactions, save_reconciled_data
        from analyze import analyze_revenue_anomalies

        # Run pipeline
        reconciled_df, ghost_settlements = reconcile_transactions()
        save_reconciled_data(reconciled_df, ghost_settlements)
        insights, anomalies = analyze_revenue_anomalies()

        # Load insights file
        insights_path = Path(test_data_paths['output_path']) / "insights.json"
        with open(insights_path, 'r') as f:
            insights_data = json.load(f)

        # Verify structure
        assert 'summary' in insights_data
        assert 'category_breakdown' in insights_data
        assert 'top_root_causes' in insights_data
        assert 'provider_performance' in insights_data
        assert 'recommendations' in insights_data

        # Verify summary contains expected fields
        assert 'total_missing_revenue_usd' in insights_data['summary']
        assert 'total_transactions_analyzed' in insights_data['summary']
        assert 'critical_issues' in insights_data['summary']

    def test_anomalies_json_structure(self, test_data_paths):
        """Test that anomalies JSON has correct structure."""
        from reconcile import reconcile_transactions, save_reconciled_data
        from analyze import analyze_revenue_anomalies

        # Run pipeline
        reconciled_df, ghost_settlements = reconcile_transactions()
        save_reconciled_data(reconciled_df, ghost_settlements)
        insights, anomalies = analyze_revenue_anomalies()

        # Load anomalies file
        anomalies_path = Path(test_data_paths['output_path']) / "anomalies.json"
        with open(anomalies_path, 'r') as f:
            anomalies_data = json.load(f)

        # Verify it's a list
        assert isinstance(anomalies_data, list)

        # If anomalies exist, verify structure
        if len(anomalies_data) > 0:
            anomaly = anomalies_data[0]
            required_fields = [
                'anomaly_id',
                'transaction_id',
                'date',
                'provider',
                'payment_method',
                'country',
                'anomaly_type',
                'severity',
                'suggested_action'
            ]

            for field in required_fields:
                assert field in anomaly, f"Required field {field} missing from anomaly"

    def test_data_consistency_across_outputs(self, test_data_paths):
        """Test data consistency between reconciled data and analysis outputs."""
        from reconcile import reconcile_transactions, save_reconciled_data
        from analyze import analyze_revenue_anomalies

        # Run pipeline
        reconciled_df, ghost_settlements = reconcile_transactions()
        save_reconciled_data(reconciled_df, ghost_settlements)
        insights, anomalies = analyze_revenue_anomalies()

        # Load reconciled data
        reconciled_path = Path(test_data_paths['output_path']) / "reconciled_data.csv"
        reconciled_data = pd.read_csv(reconciled_path)

        # Verify insights transaction count matches reconciled data
        assert insights['summary']['total_transactions_analyzed'] == len(reconciled_data)

    def test_pipeline_handles_missing_settlements(self, test_data_paths):
        """Test that pipeline correctly identifies missing settlements."""
        from reconcile import reconcile_transactions

        reconciled_df, ghost_settlements = reconcile_transactions()

        # Count missing settlements
        missing = reconciled_df[reconciled_df['settlement_status'] == 'missing']

        # Based on test fixtures, we expect 2 missing settlements (TXN_005, TXN_008)
        assert len(missing) == 2

    def test_pipeline_identifies_ghost_settlements(self, test_data_paths):
        """Test that pipeline correctly identifies ghost settlements."""
        from reconcile import reconcile_transactions

        reconciled_df, ghost_settlements = reconcile_transactions()

        # Based on test fixtures, we expect 1 ghost settlement (SET_999)
        assert len(ghost_settlements) == 1
        assert ghost_settlements['settlement_id'].iloc[0] == 'SET_999'

    def test_pipeline_detects_timing_anomalies(self, test_data_paths):
        """Test that pipeline correctly detects timing anomalies."""
        from reconcile import reconcile_transactions

        reconciled_df, ghost_settlements = reconcile_transactions()

        # Count timing anomalies
        timing_anomalies = reconciled_df[reconciled_df['timing_anomaly'] == True]

        # Based on test fixtures, we expect 1 timing anomaly (TXN_013 - 18 days)
        assert len(timing_anomalies) == 1

    def test_pipeline_calculates_expected_amounts_correctly(self, test_data_paths):
        """Test that expected settlement amounts are calculated correctly."""
        from reconcile import reconcile_transactions

        reconciled_df, ghost_settlements = reconcile_transactions()

        # Check a specific transaction (TXN_001: 100 BRL credit card)
        txn_001 = reconciled_df[reconciled_df['transaction_id'] == 'TXN_001']

        if len(txn_001) > 0:
            # Expected: 100 - (100 * 0.029 + 0.30) = 96.80
            expected = txn_001['expected_settled_amount'].iloc[0]
            assert abs(expected - 96.80) < 0.01

    def test_pipeline_matches_settlements_correctly(self, test_data_paths):
        """Test that settlements are matched to correct transactions."""
        from reconcile import reconcile_transactions

        reconciled_df, ghost_settlements = reconcile_transactions()

        # Check TXN_001 is matched to SET_001
        txn_001 = reconciled_df[reconciled_df['transaction_id'] == 'TXN_001']

        if len(txn_001) > 0:
            assert txn_001['settlement_id'].iloc[0] == 'SET_001'
            assert txn_001['settlement_status'].iloc[0] == 'matched'

    def test_pipeline_categorizes_statuses_correctly(self, test_data_paths):
        """Test that transaction statuses are categorized correctly."""
        from reconcile import reconcile_transactions

        reconciled_df, ghost_settlements = reconcile_transactions()

        # Check authorized transaction (TXN_006) is not_applicable
        txn_006 = reconciled_df[reconciled_df['transaction_id'] == 'TXN_006']
        if len(txn_006) > 0:
            assert txn_006['settlement_status'].iloc[0] == 'not_applicable'

        # Check declined transaction (TXN_007) is not_applicable
        txn_007 = reconciled_df[reconciled_df['transaction_id'] == 'TXN_007']
        if len(txn_007) > 0:
            assert txn_007['settlement_status'].iloc[0] == 'not_applicable'

    def test_analysis_generates_all_categories(self, test_data_paths):
        """Test that analysis generates all expected categories."""
        from reconcile import reconcile_transactions, save_reconciled_data
        from analyze import analyze_revenue_anomalies

        # Run pipeline
        reconciled_df, ghost_settlements = reconcile_transactions()
        save_reconciled_data(reconciled_df, ghost_settlements)
        insights, anomalies = analyze_revenue_anomalies()

        # Verify all categories exist
        expected_categories = [
            'unsettled_authorizations',
            'missing_settlements',
            'unexpected_fees',
            'chargebacks',
            'refunds',
            'timing_delays',
            'ghost_settlements'
        ]

        for category in expected_categories:
            assert category in insights['category_breakdown']

    def test_anomalies_are_prioritized(self, test_data_paths):
        """Test that anomalies are sorted by financial impact."""
        from reconcile import reconcile_transactions, save_reconciled_data
        from analyze import analyze_revenue_anomalies

        # Run pipeline
        reconciled_df, ghost_settlements = reconcile_transactions()
        save_reconciled_data(reconciled_df, ghost_settlements)
        insights, anomalies = analyze_revenue_anomalies()

        # Verify anomalies are sorted by amount_usd (descending)
        if len(anomalies) > 1:
            amounts = [a['amount_usd'] for a in anomalies]
            assert amounts == sorted(amounts, reverse=True)

    def test_pipeline_error_handling(self, tmp_path):
        """Test pipeline error handling with missing files."""
        from reconcile import load_data

        # Set paths to non-existent files
        original_txn_path = Config.TRANSACTIONS_DATA_PATH
        Config.TRANSACTIONS_DATA_PATH = str(tmp_path / "nonexistent.csv")

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            load_data()

        # Restore original path
        Config.TRANSACTIONS_DATA_PATH = original_txn_path


class TestPipelinePerformance:
    """Performance tests for pipeline execution."""

    def test_pipeline_executes_in_reasonable_time(self, test_data_paths):
        """Test that pipeline executes in reasonable time."""
        import time
        from reconcile import reconcile_transactions, save_reconciled_data
        from analyze import analyze_revenue_anomalies

        # Measure execution time
        start_time = time.time()

        reconciled_df, ghost_settlements = reconcile_transactions()
        save_reconciled_data(reconciled_df, ghost_settlements)
        insights, anomalies = analyze_revenue_anomalies()

        end_time = time.time()
        execution_time = end_time - start_time

        # Pipeline should complete in less than 10 seconds for test data
        assert execution_time < 10.0, f"Pipeline took {execution_time:.2f} seconds"


class TestDataValidation:
    """Tests for data validation and quality checks."""

    def test_no_duplicate_transaction_ids(self, test_data_paths):
        """Test that there are no duplicate transaction IDs."""
        from reconcile import reconcile_transactions

        reconciled_df, _ = reconcile_transactions()

        # Check for duplicates
        duplicates = reconciled_df['transaction_id'].duplicated().sum()
        assert duplicates == 0

    def test_all_amounts_are_positive(self, test_data_paths):
        """Test that all transaction amounts are positive."""
        from reconcile import reconcile_transactions

        reconciled_df, _ = reconcile_transactions()

        # All amounts should be positive
        assert (reconciled_df['amount'] > 0).all()

    def test_currencies_are_valid(self, test_data_paths):
        """Test that all currencies are valid."""
        from reconcile import reconcile_transactions

        reconciled_df, _ = reconcile_transactions()

        valid_currencies = ['BRL', 'MXN', 'COP', 'CLP', 'USD']
        assert reconciled_df['currency'].isin(valid_currencies).all()

    def test_settlement_dates_after_transaction_dates(self, test_data_paths):
        """Test that settlement dates are after transaction dates."""
        from reconcile import reconcile_transactions

        reconciled_df, _ = reconcile_transactions()

        # Filter for matched settlements
        matched = reconciled_df[
            (reconciled_df['settlement_status'] == 'matched') &
            (reconciled_df['settlement_date'].notna())
        ].copy()

        if len(matched) > 0:
            # Convert to datetime
            matched['timestamp'] = pd.to_datetime(matched['timestamp'])
            matched['settlement_date'] = pd.to_datetime(matched['settlement_date'])

            # Settlement date should be >= transaction date
            assert (matched['settlement_date'] >= matched['timestamp']).all()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
