"""
Settlement Reconciliation Module

This module implements the core reconciliation logic for matching transactions
to settlements, identifying anomalies, and detecting discrepancies in the
Horizon Gaming payment processing pipeline.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple
from config import Config
from fees import calculate_expected_settlement


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load transaction and settlement data from CSV files.

    Returns:
        Tuple of (transactions_df, settlements_df)

    Raises:
        FileNotFoundError: If data files don't exist
        ValueError: If data files are invalid
    """
    try:
        transactions_df = pd.read_csv(Config.TRANSACTIONS_DATA_PATH)
        settlements_df = pd.read_csv(Config.SETTLEMENTS_DATA_PATH)

        # Convert timestamp columns to datetime
        transactions_df['timestamp'] = pd.to_datetime(transactions_df['timestamp'])
        settlements_df['settlement_date'] = pd.to_datetime(settlements_df['settlement_date'])

        print(f"Loaded {len(transactions_df)} transactions")
        print(f"Loaded {len(settlements_df)} settlements")

        return transactions_df, settlements_df

    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Data files not found. Please run generate_data.py first. Error: {e}"
        )
    except Exception as e:
        raise ValueError(f"Error loading data: {e}")


def calculate_expected_amounts(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate expected settlement amounts for all transactions.

    Args:
        transactions_df: DataFrame with transaction records

    Returns:
        DataFrame with added expected_settled_amount column
    """
    transactions_df = transactions_df.copy()

    # Calculate expected settlement amount for each transaction
    transactions_df['expected_settled_amount'] = transactions_df.apply(
        lambda row: calculate_expected_settlement(row['amount'], row['payment_method']),
        axis=1
    )

    return transactions_df


def match_settlements_exact(
    transactions_df: pd.DataFrame,
    settlements_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Match settlements to transactions using exact transaction_id matching.

    Args:
        transactions_df: DataFrame with transaction records
        settlements_df: DataFrame with settlement records

    Returns:
        DataFrame with matched transaction and settlement data
    """
    # Merge on transaction_id
    matched_df = transactions_df.merge(
        settlements_df,
        on='transaction_id',
        how='left',
        suffixes=('', '_settlement')
    )

    # Rename settlement columns for clarity
    if 'provider_settlement' in matched_df.columns:
        matched_df = matched_df.drop('provider_settlement', axis=1)
    if 'currency_settlement' in matched_df.columns:
        matched_df = matched_df.drop('currency_settlement', axis=1)

    return matched_df


def calculate_discrepancies(reconciled_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate discrepancies between expected and actual settlement amounts.

    Args:
        reconciled_df: DataFrame with matched transactions and settlements

    Returns:
        DataFrame with discrepancy calculations
    """
    # Handle empty DataFrame
    if reconciled_df is None or len(reconciled_df) == 0:
        return reconciled_df

    reconciled_df = reconciled_df.copy()

    # Calculate discrepancy (only for settled transactions)
    reconciled_df['actual_settled_amount'] = reconciled_df['settled_amount']

    # Calculate absolute discrepancy
    reconciled_df['discrepancy_amount'] = np.where(
        reconciled_df['actual_settled_amount'].notna(),
        reconciled_df['expected_settled_amount'] - reconciled_df['actual_settled_amount'],
        np.nan
    )

    # Calculate discrepancy percentage
    reconciled_df['discrepancy_percent'] = np.where(
        reconciled_df['actual_settled_amount'].notna(),
        (reconciled_df['discrepancy_amount'] / reconciled_df['expected_settled_amount'] * 100),
        np.nan
    )

    return reconciled_df


def detect_timing_anomalies(reconciled_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect settlement timing anomalies based on payment method norms.

    Args:
        reconciled_df: DataFrame with matched transactions and settlements

    Returns:
        DataFrame with timing anomaly flags
    """
    # Handle empty DataFrame
    if reconciled_df is None or len(reconciled_df) == 0:
        return reconciled_df

    reconciled_df = reconciled_df.copy()

    # Calculate days to settle
    reconciled_df['days_to_settle'] = np.where(
        reconciled_df['settlement_date'].notna(),
        (reconciled_df['settlement_date'] - reconciled_df['timestamp']).dt.days,
        np.nan
    )

    # Get timing thresholds for each payment method
    def get_threshold(payment_method):
        _, _, threshold = Config.get_settlement_timing(payment_method)
        return threshold

    reconciled_df['settlement_threshold'] = reconciled_df['payment_method'].apply(get_threshold)

    # Flag timing anomalies
    reconciled_df['timing_anomaly'] = np.where(
        (reconciled_df['days_to_settle'].notna()) &
        (reconciled_df['days_to_settle'] > reconciled_df['settlement_threshold']),
        True,
        False
    )

    return reconciled_df


def classify_settlement_status(reconciled_df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify settlement status for each transaction.

    Categories:
    - matched: Settlement found with no significant discrepancy
    - missing: Captured transaction with no settlement
    - discrepancy: Settlement found but amount discrepancy > threshold
    - not_applicable: Transaction not expected to have settlement (authorized, declined, etc.)

    Args:
        reconciled_df: DataFrame with matched transactions and settlements

    Returns:
        DataFrame with settlement_status column
    """
    reconciled_df = reconciled_df.copy()

    # Define discrepancy threshold: >1% or >$1
    discrepancy_threshold_percent = 1.0
    discrepancy_threshold_amount = 1.0

    def classify_status(row):
        # Not applicable: transactions that shouldn't have settlements
        if row['status'] in ['authorized', 'declined']:
            return 'not_applicable'

        # No settlement found
        if pd.isna(row['settlement_id']):
            # Captured transactions without settlement are missing
            if row['status'] == 'captured':
                return 'missing'
            # Refunded and chargedback can be missing (acceptable)
            elif row['status'] in ['refunded', 'chargedback']:
                return 'missing_expected'
            else:
                return 'not_applicable'

        # Settlement found - check for discrepancies
        if not pd.isna(row['discrepancy_amount']):
            abs_discrepancy = abs(row['discrepancy_amount'])
            discrepancy_pct = abs(row['discrepancy_percent'])

            if abs_discrepancy > discrepancy_threshold_amount and \
               discrepancy_pct > discrepancy_threshold_percent:
                return 'discrepancy'

        # Settlement found with acceptable amounts
        return 'matched'

    reconciled_df['settlement_status'] = reconciled_df.apply(classify_status, axis=1)

    return reconciled_df


def identify_ghost_settlements(
    reconciled_df: pd.DataFrame,
    settlements_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Identify ghost settlements (settlements with no matching transaction).

    Args:
        reconciled_df: DataFrame with reconciled transactions
        settlements_df: Original settlements DataFrame

    Returns:
        DataFrame with ghost settlement records
    """
    # Get all settlement IDs that were matched to transactions
    matched_settlement_ids = set(
        reconciled_df[reconciled_df['settlement_id'].notna()]['settlement_id'].unique()
    )

    # Find settlements not in matched set
    all_settlement_ids = set(settlements_df['settlement_id'].unique())
    ghost_settlement_ids = all_settlement_ids - matched_settlement_ids

    # Extract ghost settlement records
    ghost_settlements = settlements_df[
        settlements_df['settlement_id'].isin(ghost_settlement_ids)
    ].copy()

    ghost_settlements['anomaly_type'] = 'ghost_settlement'

    print(f"Identified {len(ghost_settlements)} ghost settlements")

    return ghost_settlements


def calculate_expected_settlement_date(row) -> datetime:
    """
    Calculate expected settlement date based on transaction date and payment method.

    Args:
        row: DataFrame row with transaction data

    Returns:
        Expected settlement date
    """
    min_days, max_days, _ = Config.get_settlement_timing(row['payment_method'])
    avg_days = (min_days + max_days) / 2

    expected_date = row['timestamp'] + timedelta(days=avg_days)
    return expected_date


def reconcile_transactions() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main reconciliation function that orchestrates the full reconciliation process.

    Process:
    1. Load transaction and settlement data
    2. Calculate expected settlement amounts
    3. Match transactions to settlements
    4. Calculate discrepancies
    5. Detect timing anomalies
    6. Classify settlement status
    7. Identify ghost settlements

    Returns:
        Tuple of (reconciled_df, ghost_settlements_df)
    """
    print("=" * 60)
    print("Settlement Reconciliation Pipeline")
    print("=" * 60)
    print()

    # Step 1: Load data
    print("Step 1: Loading data...")
    transactions_df, settlements_df = load_data()
    print()

    # Step 2: Calculate expected amounts
    print("Step 2: Calculating expected settlement amounts...")
    transactions_df = calculate_expected_amounts(transactions_df)
    print(f"Calculated expected amounts for {len(transactions_df)} transactions")
    print()

    # Step 3: Match settlements
    print("Step 3: Matching transactions to settlements...")
    reconciled_df = match_settlements_exact(transactions_df, settlements_df)
    matched_count = reconciled_df['settlement_id'].notna().sum()
    print(f"Matched {matched_count} transactions to settlements")
    print()

    # Step 4: Calculate discrepancies
    print("Step 4: Calculating discrepancies...")
    reconciled_df = calculate_discrepancies(reconciled_df)
    discrepancy_count = (
        (reconciled_df['discrepancy_amount'].notna()) &
        (reconciled_df['discrepancy_amount'].abs() > 1.0)
    ).sum()
    print(f"Identified {discrepancy_count} transactions with significant discrepancies")
    print()

    # Step 5: Detect timing anomalies
    print("Step 5: Detecting timing anomalies...")
    reconciled_df = detect_timing_anomalies(reconciled_df)
    timing_anomaly_count = reconciled_df['timing_anomaly'].sum()
    print(f"Identified {timing_anomaly_count} timing anomalies")
    print()

    # Step 6: Classify settlement status
    print("Step 6: Classifying settlement status...")
    reconciled_df = classify_settlement_status(reconciled_df)

    status_counts = reconciled_df['settlement_status'].value_counts()
    print("Settlement Status Distribution:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    print()

    # Step 7: Identify ghost settlements
    print("Step 7: Identifying ghost settlements...")
    ghost_settlements = identify_ghost_settlements(reconciled_df, settlements_df)
    print()

    # Add expected settlement date for missing settlements
    reconciled_df['expected_settlement_date'] = reconciled_df.apply(
        calculate_expected_settlement_date,
        axis=1
    )

    print("=" * 60)
    print("✓ Reconciliation complete!")
    print("=" * 60)

    return reconciled_df, ghost_settlements


def save_reconciled_data(
    reconciled_df: pd.DataFrame,
    ghost_settlements: pd.DataFrame,
    output_path: str = None
):
    """
    Save reconciled data to CSV file.

    Args:
        reconciled_df: Reconciled transaction data
        ghost_settlements: Ghost settlement records
        output_path: Optional output file path
    """
    if output_path is None:
        output_path = f"{Config.OUTPUT_PATH}reconciled_data.csv"

    # Ensure output directory exists
    Config.ensure_output_directory()

    # Save reconciled data
    reconciled_df.to_csv(output_path, index=False)
    print(f"Reconciled data saved to: {output_path}")

    # Save ghost settlements separately
    ghost_path = f"{Config.OUTPUT_PATH}ghost_settlements.csv"
    ghost_settlements.to_csv(ghost_path, index=False)
    print(f"Ghost settlements saved to: {ghost_path}")


if __name__ == '__main__':
    # Run reconciliation
    reconciled_df, ghost_settlements = reconcile_transactions()

    # Save results
    print()
    print("Saving reconciled data...")
    save_reconciled_data(reconciled_df, ghost_settlements)
    print()
    print("✓ Pipeline execution complete!")
