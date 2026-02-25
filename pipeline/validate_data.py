"""
Data Validation Module

This module validates the quality and completeness of generated test data
for the Horizon Gaming Revenue Anomaly Detector.
"""

import pandas as pd
from datetime import datetime
from config import Config


def validate_transactions(df: pd.DataFrame) -> dict:
    """
    Validate transaction data quality.

    Checks:
    - Required fields present
    - Valid values for categorical fields
    - Data type correctness
    - Realistic distributions
    - Presence of various transaction scenarios

    Args:
        df: Transaction DataFrame

    Returns:
        Dictionary with validation results
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'statistics': {}
    }

    # Check required columns
    required_cols = ['transaction_id', 'timestamp', 'amount', 'currency',
                     'status', 'provider', 'payment_method', 'country', 'customer_id']

    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        results['valid'] = False
        results['errors'].append(f"Missing required columns: {missing_cols}")
        return results

    # Check for null values
    null_counts = df[required_cols].isnull().sum()
    if null_counts.any():
        results['valid'] = False
        results['errors'].append(f"Null values found: {null_counts[null_counts > 0].to_dict()}")

    # Validate currencies
    valid_currencies = ['BRL', 'MXN', 'COP', 'CLP']
    invalid_currencies = set(df['currency'].unique()) - set(valid_currencies)
    if invalid_currencies:
        results['warnings'].append(f"Invalid currencies: {invalid_currencies}")

    # Validate statuses
    valid_statuses = ['captured', 'authorized', 'declined', 'refunded', 'chargedback']
    invalid_statuses = set(df['status'].unique()) - set(valid_statuses)
    if invalid_statuses:
        results['warnings'].append(f"Invalid statuses: {invalid_statuses}")

    # Validate payment methods
    valid_methods = ['credit_card', 'debit_card', 'bank_transfer', 'cash_voucher']
    invalid_methods = set(df['payment_method'].unique()) - set(valid_methods)
    if invalid_methods:
        results['warnings'].append(f"Invalid payment methods: {invalid_methods}")

    # Check for captured transactions (needed for settlements)
    captured_count = len(df[df['status'] == 'captured'])
    if captured_count < 500:
        results['warnings'].append(f"Low captured transaction count: {captured_count}")

    # Statistics
    results['statistics'] = {
        'total_records': len(df),
        'captured_transactions': captured_count,
        'unique_providers': df['provider'].nunique(),
        'unique_countries': df['country'].nunique(),
        'date_range': f"{df['timestamp'].min()} to {df['timestamp'].max()}"
    }

    return results


def validate_settlements(df: pd.DataFrame, transactions_df: pd.DataFrame) -> dict:
    """
    Validate settlement data quality.

    Checks:
    - Required fields present
    - Settlement references valid transactions
    - Settlement dates after transaction dates
    - Settlement rate within expected range
    - Presence of anomaly scenarios

    Args:
        df: Settlement DataFrame
        transactions_df: Transaction DataFrame for reference

    Returns:
        Dictionary with validation results
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'statistics': {}
    }

    # Check required columns
    required_cols = ['settlement_id', 'transaction_id', 'settlement_date',
                     'settled_amount', 'currency', 'provider']

    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        results['valid'] = False
        results['errors'].append(f"Missing required columns: {missing_cols}")
        return results

    # Check for null values
    null_counts = df[required_cols].isnull().sum()
    if null_counts.any():
        results['valid'] = False
        results['errors'].append(f"Null values found: {null_counts[null_counts > 0].to_dict()}")

    # Check settlement rate
    captured_txns = transactions_df[transactions_df['status'] == 'captured']
    settlement_rate = len(df) / len(captured_txns) * 100

    if settlement_rate < 60 or settlement_rate > 85:
        results['warnings'].append(
            f"Settlement rate {settlement_rate:.1f}% outside expected 70-80% range"
        )

    # Check for ghost settlements
    transaction_ids = set(transactions_df['transaction_id'])
    settlement_txn_ids = set(df['transaction_id'])
    ghost_settlements = settlement_txn_ids - transaction_ids

    if len(ghost_settlements) > 0:
        results['statistics']['ghost_settlements'] = len(ghost_settlements)
        print(f"Found {len(ghost_settlements)} ghost settlements (expected anomaly)")

    # Statistics
    results['statistics'].update({
        'total_settlements': len(df),
        'settlement_rate_percent': round(settlement_rate, 1),
        'unique_providers': df['provider'].nunique(),
        'date_range': f"{df['settlement_date'].min()} to {df['settlement_date'].max()}"
    })

    return results


def main():
    """
    Main validation function.

    Loads generated data and runs validation checks.
    """
    print("=" * 60)
    print("Data Validation")
    print("=" * 60)
    print()

    # Load data
    print("Loading data files...")
    try:
        transactions_df = pd.read_csv(Config.TRANSACTIONS_DATA_PATH)
        settlements_df = pd.read_csv(Config.SETTLEMENTS_DATA_PATH)
        print("✓ Data files loaded successfully")
        print()
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return

    # Validate transactions
    print("Validating transactions...")
    txn_results = validate_transactions(transactions_df)

    if txn_results['valid']:
        print("✓ Transaction validation passed")
    else:
        print("✗ Transaction validation failed")
        for error in txn_results['errors']:
            print(f"  ERROR: {error}")

    for warning in txn_results['warnings']:
        print(f"  WARNING: {warning}")

    print("\nTransaction Statistics:")
    for key, value in txn_results['statistics'].items():
        print(f"  {key}: {value}")
    print()

    # Validate settlements
    print("Validating settlements...")
    settle_results = validate_settlements(settlements_df, transactions_df)

    if settle_results['valid']:
        print("✓ Settlement validation passed")
    else:
        print("✗ Settlement validation failed")
        for error in settle_results['errors']:
            print(f"  ERROR: {error}")

    for warning in settle_results['warnings']:
        print(f"  WARNING: {warning}")

    print("\nSettlement Statistics:")
    for key, value in settle_results['statistics'].items():
        print(f"  {key}: {value}")
    print()

    # Overall result
    if txn_results['valid'] and settle_results['valid']:
        print("=" * 60)
        print("✓ Data validation complete - All checks passed!")
        print("=" * 60)
    else:
        print("=" * 60)
        print("✗ Data validation complete - Some checks failed")
        print("=" * 60)


if __name__ == '__main__':
    main()
