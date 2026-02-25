"""
Test Data Generation Module

This module generates realistic test transaction and settlement data for the
Horizon Gaming Revenue Anomaly Detector. It creates scenarios that include
normal transactions, missing settlements, fee discrepancies, timing anomalies,
and ghost settlements.

Target: 500-1000 transactions with ~70-80% settlement rate and major anomalies.
"""

import random
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
from typing import List, Dict
from fees import calculate_expected_settlement
from config import Config

# Initialize Faker with seed for reproducibility
fake = Faker()
Faker.seed(42)
random.seed(42)

# Payment providers (distribution weights)
PROVIDERS = {
    'PayBridge': 0.25,
    'LatamPay': 0.25,
    'GlobalSettle': 0.20,
    'FastPay': 0.20,
    'VoucherPro': 0.10
}

# Countries and their currencies (distribution weights)
COUNTRIES = {
    'Brazil': {'currency': 'BRL', 'weight': 0.40},
    'Mexico': {'currency': 'MXN', 'weight': 0.30},
    'Colombia': {'currency': 'COP', 'weight': 0.20},
    'Chile': {'currency': 'CLP', 'weight': 0.10}
}

# Transaction statuses (distribution weights)
STATUSES = {
    'captured': 0.70,     # Successfully captured transactions
    'authorized': 0.15,   # Authorized but not captured (abandoned carts)
    'declined': 0.10,     # Declined transactions
    'refunded': 0.03,     # Refunded transactions
    'chargedback': 0.02   # Chargedback transactions
}

# Payment methods (distribution weights)
PAYMENT_METHODS = {
    'credit_card': 0.50,
    'debit_card': 0.30,
    'bank_transfer': 0.15,
    'cash_voucher': 0.05
}


def weighted_random_choice(options: Dict[str, float]) -> str:
    """
    Select a random choice based on weighted probabilities.

    Args:
        options: Dictionary mapping choices to their probability weights

    Returns:
        Selected choice
    """
    choices = list(options.keys())
    weights = list(options.values())
    return random.choices(choices, weights=weights, k=1)[0]


def generate_transaction_amount(country: str) -> float:
    """
    Generate realistic transaction amount based on country currency.

    Args:
        country: Country name

    Returns:
        Transaction amount in local currency
    """
    currency = COUNTRIES[country]['currency']

    # Base amount in USD equivalent: $10-500
    usd_amount = random.uniform(10, 500)

    # Convert to local currency (inverse of exchange rate)
    rate = Config.get_exchange_rate(currency)
    local_amount = usd_amount / rate

    # Round to 2 decimal places
    return round(local_amount, 2)


def generate_transactions(count: int = 1000) -> pd.DataFrame:
    """
    Generate realistic transaction data.

    Creates transactions with various statuses, payment methods, and providers.
    Includes strategic anomalies for testing:
    - One provider with high missing settlement rate
    - Various transaction scenarios across countries

    Args:
        count: Number of transactions to generate

    Returns:
        DataFrame with transaction records
    """
    transactions = []
    start_date = datetime.now() - timedelta(days=30)

    # Provider that will have anomalies (50+ transactions, no settlements)
    anomaly_provider = 'GlobalSettle'

    for i in range(count):
        # Generate transaction ID
        transaction_id = f"TXN_{str(i+1).zfill(6)}"

        # Random timestamp within last 30 days
        days_ago = random.uniform(0, 30)
        timestamp = start_date + timedelta(days=days_ago)

        # Select country and currency
        country = weighted_random_choice({k: v['weight'] for k, v in COUNTRIES.items()})
        currency = COUNTRIES[country]['currency']

        # Generate amount
        amount = generate_transaction_amount(country)

        # Select payment method
        payment_method = weighted_random_choice(PAYMENT_METHODS)

        # Select provider
        provider = weighted_random_choice(PROVIDERS)

        # Select status
        status = weighted_random_choice(STATUSES)

        # Create anomaly cluster: 60 captured transactions from GlobalSettle
        # in week 2-3 that will have NO settlements
        if i >= 200 and i < 260 and provider == anomaly_provider:
            status = 'captured'  # Force captured status for anomaly
            timestamp = start_date + timedelta(days=random.uniform(7, 21))

        # Generate customer ID
        customer_id = f"CUST_{random.randint(1000, 9999)}"

        transaction = {
            'transaction_id': transaction_id,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'amount': amount,
            'currency': currency,
            'status': status,
            'provider': provider,
            'payment_method': payment_method,
            'country': country,
            'customer_id': customer_id
        }

        transactions.append(transaction)

    return pd.DataFrame(transactions)


def generate_settlements(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate settlement records based on transaction data.

    Settlement logic:
    - Only captured transactions can have settlements
    - 70-80% of captured transactions receive settlements
    - Settlement dates follow payment method timing norms
    - Some settlements have fee discrepancies (incorrect deductions)
    - Some settlements are delayed beyond normal timing
    - Includes 2-3 ghost settlements (no matching transaction)

    Args:
        transactions_df: DataFrame with transaction records

    Returns:
        DataFrame with settlement records
    """
    settlements = []
    settlement_id_counter = 1

    # Filter only captured transactions
    captured_txns = transactions_df[transactions_df['status'] == 'captured'].copy()

    # Anomaly: GlobalSettle transactions between days 7-21 have NO settlements
    anomaly_mask = (
        (captured_txns['provider'] == 'GlobalSettle') &
        (pd.to_datetime(captured_txns['timestamp']) >=
         (datetime.now() - timedelta(days=23))) &
        (pd.to_datetime(captured_txns['timestamp']) <=
         (datetime.now() - timedelta(days=9)))
    )

    # Separate anomaly transactions from normal ones
    anomaly_txns = captured_txns[anomaly_mask]
    normal_txns = captured_txns[~anomaly_mask]

    print(f"Total captured transactions: {len(captured_txns)}")
    print(f"Anomaly transactions (no settlement): {len(anomaly_txns)}")
    print(f"Normal transactions: {len(normal_txns)}")

    # Generate settlements for 75% of normal captured transactions
    settlement_rate = 0.75
    txns_to_settle = normal_txns.sample(frac=settlement_rate, random_state=42)

    for _, txn in txns_to_settle.iterrows():
        settlement_id = f"SET_{str(settlement_id_counter).zfill(6)}"
        settlement_id_counter += 1

        # Get settlement timing based on payment method
        min_days, max_days, _ = Config.get_settlement_timing(txn['payment_method'])

        # Some transactions have delayed settlements (timing anomaly)
        if random.random() < 0.10:  # 10% have delays
            # Delayed by 50-100% beyond max
            settlement_days = max_days + random.uniform(max_days * 0.5, max_days)
        else:
            # Normal timing
            settlement_days = random.uniform(min_days, max_days)

        # Calculate settlement date
        txn_date = datetime.strptime(txn['timestamp'], '%Y-%m-%d %H:%M:%S')
        settlement_date = txn_date + timedelta(days=settlement_days)

        # Calculate expected settled amount
        expected_amount = calculate_expected_settlement(txn['amount'], txn['payment_method'])

        # Some settlements have fee discrepancies (5% of settlements)
        if random.random() < 0.05:
            # Incorrect fee deduction: ±10-20% variance
            variance = random.uniform(-0.20, -0.10)  # More fees deducted
            settled_amount = expected_amount * (1 + variance)
        else:
            # Correct fee deduction (with minor rounding differences)
            settled_amount = expected_amount + random.uniform(-0.02, 0.02)

        settled_amount = round(settled_amount, 2)

        settlement = {
            'settlement_id': settlement_id,
            'transaction_id': txn['transaction_id'],
            'settlement_date': settlement_date.strftime('%Y-%m-%d %H:%M:%S'),
            'settled_amount': settled_amount,
            'currency': txn['currency'],
            'provider': txn['provider']
        }

        settlements.append(settlement)

    # Add 3 ghost settlements (settlements with no matching transaction)
    for i in range(3):
        settlement_id = f"SET_{str(settlement_id_counter).zfill(6)}"
        settlement_id_counter += 1

        # Ghost settlements reference non-existent transactions
        ghost_txn_id = f"TXN_999{str(i+1).zfill(3)}"

        # Random date in last 30 days
        settlement_date = datetime.now() - timedelta(days=random.uniform(0, 30))

        # Random provider and currency
        provider = weighted_random_choice(PROVIDERS)
        country = weighted_random_choice({k: v['weight'] for k, v in COUNTRIES.items()})
        currency = COUNTRIES[country]['currency']

        # Random amount
        amount = generate_transaction_amount(country)

        settlement = {
            'settlement_id': settlement_id,
            'transaction_id': ghost_txn_id,
            'settlement_date': settlement_date.strftime('%Y-%m-%d %H:%M:%S'),
            'settled_amount': amount,
            'currency': currency,
            'provider': provider
        }

        settlements.append(settlement)

    settlements_df = pd.DataFrame(settlements)
    print(f"Total settlements generated: {len(settlements_df)}")
    print(f"Settlement rate: {len(settlements_df) / len(captured_txns) * 100:.1f}%")

    return settlements_df


def main():
    """
    Main execution function for test data generation.

    Generates transactions and settlements, then saves to CSV files.
    """
    print("=" * 60)
    print("Horizon Gaming - Test Data Generation")
    print("=" * 60)
    print()

    # Generate transactions
    print("Generating transaction data...")
    num_transactions = 1000
    transactions_df = generate_transactions(num_transactions)
    print(f"Generated {len(transactions_df)} transactions")
    print()

    # Generate settlements
    print("Generating settlement data...")
    settlements_df = generate_settlements(transactions_df)
    print()

    # Save to CSV files
    print("Saving data files...")
    transactions_path = Config.TRANSACTIONS_DATA_PATH
    settlements_path = Config.SETTLEMENTS_DATA_PATH

    transactions_df.to_csv(transactions_path, index=False)
    settlements_df.to_csv(settlements_path, index=False)

    print(f"Transactions saved to: {transactions_path}")
    print(f"Settlements saved to: {settlements_path}")
    print()

    # Summary statistics
    print("=" * 60)
    print("Data Summary")
    print("=" * 60)
    print(f"Total transactions: {len(transactions_df)}")
    print(f"Total settlements: {len(settlements_df)}")
    print()

    print("Transaction Status Distribution:")
    status_counts = transactions_df['status'].value_counts()
    for status, count in status_counts.items():
        print(f"  {status}: {count} ({count/len(transactions_df)*100:.1f}%)")
    print()

    print("Payment Method Distribution:")
    method_counts = transactions_df['payment_method'].value_counts()
    for method, count in method_counts.items():
        print(f"  {method}: {count} ({count/len(transactions_df)*100:.1f}%)")
    print()

    print("Provider Distribution:")
    provider_counts = transactions_df['provider'].value_counts()
    for provider, count in provider_counts.items():
        print(f"  {provider}: {count} ({count/len(transactions_df)*100:.1f}%)")
    print()

    print("Country Distribution:")
    country_counts = transactions_df['country'].value_counts()
    for country, count in country_counts.items():
        print(f"  {country}: {count} ({count/len(transactions_df)*100:.1f}%)")
    print()

    # Calculate total transaction value in USD
    total_usd = 0
    for _, txn in transactions_df.iterrows():
        usd_amount = txn['amount'] * Config.get_exchange_rate(txn['currency'])
        total_usd += usd_amount

    print(f"Total transaction value: ${total_usd:,.2f} USD")
    print()

    print("✓ Test data generation complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
