"""
Revenue Anomaly Analysis Module

This module implements analysis and insights generation for the Horizon Gaming
Revenue Anomaly Detector. It categorizes missing revenue, identifies patterns,
and generates actionable recommendations.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from typing import Dict, List
from config import Config
from fees import convert_to_usd


def load_reconciled_data() -> pd.DataFrame:
    """
    Load reconciled data from CSV file.

    Returns:
        DataFrame with reconciled transaction data
    """
    reconciled_path = f"{Config.OUTPUT_PATH}reconciled_data.csv"
    df = pd.read_csv(reconciled_path)

    # Convert date columns
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    if 'settlement_date' in df.columns:
        df['settlement_date'] = pd.to_datetime(df['settlement_date'])

    return df


def calculate_aggregate_metrics(reconciled_df: pd.DataFrame) -> Dict:
    """
    Calculate aggregate metrics across various dimensions.

    Aggregates by:
    - Provider
    - Payment method
    - Country
    - Time period (daily/weekly)

    Args:
        reconciled_df: DataFrame with reconciled transaction data

    Returns:
        Dictionary with aggregate metrics
    """
    metrics = {}

    # Overall metrics
    total_transactions = len(reconciled_df)
    total_amount = reconciled_df['amount'].sum()

    # Convert to USD
    reconciled_df['amount_usd'] = reconciled_df.apply(
        lambda row: convert_to_usd(row['amount'], row['currency']),
        axis=1
    )

    total_amount_usd = reconciled_df['amount_usd'].sum()

    # Settled amounts
    settled_transactions = reconciled_df[reconciled_df['settlement_status'] == 'matched']
    total_settled_usd = settled_transactions.apply(
        lambda row: convert_to_usd(row['actual_settled_amount'], row['currency'])
        if pd.notna(row['actual_settled_amount']) else 0,
        axis=1
    ).sum()

    # Missing revenue (captured but not settled)
    missing_settlements = reconciled_df[reconciled_df['settlement_status'] == 'missing']
    missing_revenue_usd = missing_settlements['amount_usd'].sum()

    # Discrepancy amounts
    discrepancy_transactions = reconciled_df[reconciled_df['settlement_status'] == 'discrepancy']
    discrepancy_amount_usd = discrepancy_transactions.apply(
        lambda row: convert_to_usd(abs(row['discrepancy_amount']), row['currency'])
        if pd.notna(row['discrepancy_amount']) else 0,
        axis=1
    ).sum()

    metrics['overall'] = {
        'total_transactions': int(total_transactions),
        'total_amount_usd': round(float(total_amount_usd), 2),
        'total_settled_usd': round(float(total_settled_usd), 2),
        'missing_revenue_usd': round(float(missing_revenue_usd), 2),
        'discrepancy_amount_usd': round(float(discrepancy_amount_usd), 2),
        'total_discrepancy_usd': round(float(missing_revenue_usd + discrepancy_amount_usd), 2)
    }

    # Provider metrics
    provider_metrics = []
    for provider in reconciled_df['provider'].unique():
        provider_data = reconciled_df[reconciled_df['provider'] == provider]

        provider_total_usd = provider_data['amount_usd'].sum()
        provider_missing = provider_data[provider_data['settlement_status'] == 'missing']
        provider_missing_usd = provider_missing['amount_usd'].sum()

        provider_metrics.append({
            'provider': provider,
            'total_transactions': int(len(provider_data)),
            'total_volume_usd': round(float(provider_total_usd), 2),
            'missing_settlements': int(len(provider_missing)),
            'missing_revenue_usd': round(float(provider_missing_usd), 2),
            'discrepancy_rate_percent': round(
                float(provider_missing_usd / provider_total_usd * 100) if provider_total_usd > 0 else 0,
                2
            )
        })

    metrics['by_provider'] = sorted(provider_metrics, key=lambda x: x['missing_revenue_usd'], reverse=True)

    # Payment method metrics
    method_metrics = []
    for method in reconciled_df['payment_method'].unique():
        method_data = reconciled_df[reconciled_df['payment_method'] == method]

        method_total_usd = method_data['amount_usd'].sum()
        method_missing = method_data[method_data['settlement_status'] == 'missing']
        method_missing_usd = method_missing['amount_usd'].sum()

        method_metrics.append({
            'payment_method': method,
            'total_transactions': int(len(method_data)),
            'total_volume_usd': round(float(method_total_usd), 2),
            'missing_settlements': int(len(method_missing)),
            'missing_revenue_usd': round(float(method_missing_usd), 2),
            'discrepancy_rate_percent': round(
                float(method_missing_usd / method_total_usd * 100) if method_total_usd > 0 else 0,
                2
            )
        })

    metrics['by_payment_method'] = sorted(method_metrics, key=lambda x: x['missing_revenue_usd'], reverse=True)

    # Country metrics
    country_metrics = []
    for country in reconciled_df['country'].unique():
        country_data = reconciled_df[reconciled_df['country'] == country]

        country_total_usd = country_data['amount_usd'].sum()
        country_missing = country_data[country_data['settlement_status'] == 'missing']
        country_missing_usd = country_missing['amount_usd'].sum()

        country_metrics.append({
            'country': country,
            'total_transactions': int(len(country_data)),
            'total_volume_usd': round(float(country_total_usd), 2),
            'missing_settlements': int(len(country_missing)),
            'missing_revenue_usd': round(float(country_missing_usd), 2),
            'discrepancy_rate_percent': round(
                float(country_missing_usd / country_total_usd * 100) if country_total_usd > 0 else 0,
                2
            )
        })

    metrics['by_country'] = sorted(country_metrics, key=lambda x: x['missing_revenue_usd'], reverse=True)

    # Time series metrics (daily)
    reconciled_df['date'] = reconciled_df['timestamp'].dt.date
    daily_metrics = []

    for date in sorted(reconciled_df['date'].unique()):
        daily_data = reconciled_df[reconciled_df['date'] == date]

        daily_total_usd = daily_data['amount_usd'].sum()
        daily_missing = daily_data[daily_data['settlement_status'] == 'missing']
        daily_missing_usd = daily_missing['amount_usd'].sum()

        daily_metrics.append({
            'date': str(date),
            'total_transactions': int(len(daily_data)),
            'total_volume_usd': round(float(daily_total_usd), 2),
            'missing_revenue_usd': round(float(daily_missing_usd), 2)
        })

    metrics['time_series'] = daily_metrics

    return metrics


def categorize_revenue(reconciled_df: pd.DataFrame) -> Dict:
    """
    Categorize missing revenue into defined buckets.

    Categories:
    - Unsettled authorizations: Approved but never captured (expected)
    - Missing settlements: Captured but no settlement record (RED FLAG)
    - Unexpected fees: Settled amount discrepancies
    - Chargebacks: Transactions with chargedback status
    - Refunds: Transactions with refunded status
    - Timing delays: Settlements significantly delayed
    - Ghost settlements: Settlements with no matching transaction

    Args:
        reconciled_df: DataFrame with reconciled transaction data

    Returns:
        Dictionary with categorized revenue impacts
    """
    categories = {}

    # Add USD amounts
    reconciled_df['amount_usd'] = reconciled_df.apply(
        lambda row: convert_to_usd(row['amount'], row['currency']),
        axis=1
    )

    # 1. Unsettled authorizations (not concerning - abandoned carts)
    unsettled_auth = reconciled_df[reconciled_df['status'] == 'authorized']
    categories['unsettled_authorizations'] = {
        'count': int(len(unsettled_auth)),
        'amount_usd': round(float(unsettled_auth['amount_usd'].sum()), 2),
        'severity': 'low',
        'description': 'Authorized but not captured transactions (abandoned carts - expected)'
    }

    # 2. Missing settlements (RED FLAG)
    missing_settlements = reconciled_df[reconciled_df['settlement_status'] == 'missing']
    categories['missing_settlements'] = {
        'count': int(len(missing_settlements)),
        'amount_usd': round(float(missing_settlements['amount_usd'].sum()), 2),
        'severity': 'critical',
        'description': 'Captured transactions with no settlement record'
    }

    # 3. Unexpected fees
    fee_discrepancies = reconciled_df[reconciled_df['settlement_status'] == 'discrepancy']
    fee_discrepancy_usd = fee_discrepancies.apply(
        lambda row: convert_to_usd(abs(row['discrepancy_amount']), row['currency'])
        if pd.notna(row['discrepancy_amount']) else 0,
        axis=1
    ).sum()
    categories['unexpected_fees'] = {
        'count': int(len(fee_discrepancies)),
        'amount_usd': round(float(fee_discrepancy_usd), 2),
        'severity': 'high',
        'description': 'Settlement amounts differ from expected fees'
    }

    # 4. Chargebacks
    chargebacks = reconciled_df[reconciled_df['status'] == 'chargedback']
    categories['chargebacks'] = {
        'count': int(len(chargebacks)),
        'amount_usd': round(float(chargebacks['amount_usd'].sum()), 2),
        'severity': 'medium',
        'description': 'Transactions reversed due to customer disputes'
    }

    # 5. Refunds
    refunds = reconciled_df[reconciled_df['status'] == 'refunded']
    categories['refunds'] = {
        'count': int(len(refunds)),
        'amount_usd': round(float(refunds['amount_usd'].sum()), 2),
        'severity': 'low',
        'description': 'Transactions refunded to customers'
    }

    # 6. Timing delays
    timing_delays = reconciled_df[reconciled_df['timing_anomaly'] == True]
    categories['timing_delays'] = {
        'count': int(len(timing_delays)),
        'amount_usd': round(float(timing_delays['amount_usd'].sum()), 2),
        'severity': 'medium',
        'description': 'Settlements delayed beyond expected timeframe'
    }

    # 7. Ghost settlements
    try:
        ghost_path = f"{Config.OUTPUT_PATH}ghost_settlements.csv"
        ghost_df = pd.read_csv(ghost_path)
        ghost_df['amount_usd'] = ghost_df.apply(
            lambda row: convert_to_usd(row['settled_amount'], row['currency']),
            axis=1
        )
        categories['ghost_settlements'] = {
            'count': int(len(ghost_df)),
            'amount_usd': round(float(ghost_df['amount_usd'].sum()), 2),
            'severity': 'high',
            'description': 'Settlements with no matching transaction record'
        }
    except:
        categories['ghost_settlements'] = {
            'count': 0,
            'amount_usd': 0.0,
            'severity': 'high',
            'description': 'Settlements with no matching transaction record'
        }

    return categories


def identify_patterns(reconciled_df: pd.DataFrame, categories: Dict) -> List[str]:
    """
    Identify high-risk patterns in the data.

    Analyzes:
    - Provider performance
    - Payment method reliability
    - Geographic patterns
    - Temporal patterns

    Args:
        reconciled_df: DataFrame with reconciled transaction data
        categories: Categorized revenue impact data

    Returns:
        List of pattern insights
    """
    patterns = []

    # Add USD amounts
    reconciled_df['amount_usd'] = reconciled_df.apply(
        lambda row: convert_to_usd(row['amount'], row['currency']),
        axis=1
    )

    # Pattern 1: Provider with highest missing settlement rate
    provider_analysis = reconciled_df.groupby('provider').agg({
        'transaction_id': 'count',
        'amount_usd': 'sum'
    }).reset_index()
    provider_analysis.columns = ['provider', 'txn_count', 'total_usd']

    missing_by_provider = reconciled_df[
        reconciled_df['settlement_status'] == 'missing'
    ].groupby('provider')['amount_usd'].sum().reset_index()
    missing_by_provider.columns = ['provider', 'missing_usd']

    provider_analysis = provider_analysis.merge(missing_by_provider, on='provider', how='left')
    provider_analysis['missing_usd'] = provider_analysis['missing_usd'].fillna(0)
    provider_analysis['missing_rate'] = (
        provider_analysis['missing_usd'] / provider_analysis['total_usd'] * 100
    )

    worst_provider = provider_analysis.nlargest(1, 'missing_rate').iloc[0]
    patterns.append(
        f"Provider '{worst_provider['provider']}' has the highest missing settlement rate at "
        f"{worst_provider['missing_rate']:.1f}% (${worst_provider['missing_usd']:,.2f} USD)"
    )

    # Pattern 2: Payment method with most delays
    if 'timing_anomaly' in reconciled_df.columns:
        timing_by_method = reconciled_df[
            reconciled_df['timing_anomaly'] == True
        ].groupby('payment_method').size().reset_index(name='delay_count')

        if len(timing_by_method) > 0:
            worst_method = timing_by_method.nlargest(1, 'delay_count').iloc[0]
            patterns.append(
                f"Payment method '{worst_method['payment_method']}' has the most timing delays "
                f"with {worst_method['delay_count']} delayed settlements"
            )

    # Pattern 3: Country with highest discrepancy rate
    country_analysis = reconciled_df.groupby('country')['amount_usd'].sum().reset_index()
    country_analysis.columns = ['country', 'total_usd']

    missing_by_country = reconciled_df[
        reconciled_df['settlement_status'] == 'missing'
    ].groupby('country')['amount_usd'].sum().reset_index()
    missing_by_country.columns = ['country', 'missing_usd']

    country_analysis = country_analysis.merge(missing_by_country, on='country', how='left')
    country_analysis['missing_usd'] = country_analysis['missing_usd'].fillna(0)
    country_analysis['missing_rate'] = (
        country_analysis['missing_usd'] / country_analysis['total_usd'] * 100
    )

    worst_country = country_analysis.nlargest(1, 'missing_rate').iloc[0]
    patterns.append(
        f"Country '{worst_country['country']}' has the highest discrepancy rate at "
        f"{worst_country['missing_rate']:.1f}% (${worst_country['missing_usd']:,.2f} USD)"
    )

    # Pattern 4: Time period with elevated issues
    reconciled_df['week'] = reconciled_df['timestamp'].dt.isocalendar().week
    weekly_missing = reconciled_df[
        reconciled_df['settlement_status'] == 'missing'
    ].groupby('week').size().reset_index(name='missing_count')

    if len(weekly_missing) > 0:
        worst_week = weekly_missing.nlargest(1, 'missing_count').iloc[0]
        patterns.append(
            f"Week {worst_week['week']} has the highest number of missing settlements "
            f"with {worst_week['missing_count']} unmatched transactions"
        )

    # Pattern 5: Critical category impact
    critical_categories = [k for k, v in categories.items() if v['severity'] == 'critical']
    if critical_categories:
        for cat in critical_categories:
            if categories[cat]['amount_usd'] > 0:
                patterns.append(
                    f"Critical issue: {cat.replace('_', ' ').title()} accounts for "
                    f"${categories[cat]['amount_usd']:,.2f} USD in missing revenue"
                )

    return patterns[:5]  # Return top 5 patterns


def generate_prioritized_anomalies(reconciled_df: pd.DataFrame) -> List[Dict]:
    """
    Generate prioritized list of anomalies ranked by financial impact.

    Args:
        reconciled_df: DataFrame with reconciled transaction data

    Returns:
        List of anomaly records with suggested actions
    """
    anomalies = []

    # Add USD amounts
    reconciled_df['amount_usd'] = reconciled_df.apply(
        lambda row: convert_to_usd(row['amount'], row['currency']),
        axis=1
    )

    # Missing settlements (highest priority)
    missing = reconciled_df[reconciled_df['settlement_status'] == 'missing'].copy()
    for _, row in missing.iterrows():
        anomalies.append({
            'anomaly_id': f"ANO_{len(anomalies)+1:04d}",
            'transaction_id': row['transaction_id'],
            'date': row['timestamp'].strftime('%Y-%m-%d'),
            'provider': row['provider'],
            'payment_method': row['payment_method'],
            'country': row['country'],
            'anomaly_type': 'missing_settlement',
            'category': 'missing_settlements',
            'amount': round(float(row['amount']), 2),
            'currency': row['currency'],
            'amount_usd': round(float(row['amount_usd']), 2),
            'severity': 'critical',
            'suggested_action': f"Contact {row['provider']} to investigate missing settlement for transaction {row['transaction_id']}"
        })

    # Fee discrepancies
    discrepancies = reconciled_df[reconciled_df['settlement_status'] == 'discrepancy'].copy()
    for _, row in discrepancies.iterrows():
        discrepancy_usd = convert_to_usd(abs(row['discrepancy_amount']), row['currency'])
        anomalies.append({
            'anomaly_id': f"ANO_{len(anomalies)+1:04d}",
            'transaction_id': row['transaction_id'],
            'date': row['timestamp'].strftime('%Y-%m-%d'),
            'provider': row['provider'],
            'payment_method': row['payment_method'],
            'country': row['country'],
            'anomaly_type': 'fee_discrepancy',
            'category': 'unexpected_fees',
            'amount': round(float(row['amount']), 2),
            'expected_amount': round(float(row['expected_settled_amount']), 2),
            'actual_amount': round(float(row['actual_settled_amount']), 2),
            'discrepancy': round(float(row['discrepancy_amount']), 2),
            'currency': row['currency'],
            'amount_usd': round(float(discrepancy_usd), 2),
            'severity': 'high',
            'suggested_action': f"Review fee agreement with {row['provider']} for unexpected charges"
        })

    # Timing anomalies
    timing = reconciled_df[reconciled_df['timing_anomaly'] == True].copy()
    for _, row in timing.iterrows():
        anomalies.append({
            'anomaly_id': f"ANO_{len(anomalies)+1:04d}",
            'transaction_id': row['transaction_id'],
            'date': row['timestamp'].strftime('%Y-%m-%d'),
            'provider': row['provider'],
            'payment_method': row['payment_method'],
            'country': row['country'],
            'anomaly_type': 'timing_delay',
            'category': 'timing_delays',
            'amount': round(float(row['amount']), 2),
            'currency': row['currency'],
            'amount_usd': round(float(row['amount_usd']), 2),
            'days_delayed': int(row['days_to_settle']) if pd.notna(row['days_to_settle']) else 0,
            'severity': 'medium',
            'suggested_action': f"Escalate delayed settlement with {row['provider']} (transaction >10 days old)"
        })

    # Sort by financial impact (USD amount)
    anomalies.sort(key=lambda x: x['amount_usd'], reverse=True)

    # Return top 50 anomalies
    return anomalies[:50]


def generate_insights_summary(
    metrics: Dict,
    categories: Dict,
    patterns: List[str],
    reconciled_df: pd.DataFrame
) -> Dict:
    """
    Generate executive summary with insights and recommendations.

    Args:
        metrics: Aggregate metrics
        categories: Categorized revenue data
        patterns: Identified patterns
        reconciled_df: DataFrame with reconciled transaction data

    Returns:
        Dictionary with comprehensive insights
    """
    # Calculate total missing revenue
    total_missing = categories['missing_settlements']['amount_usd']
    total_fee_discrepancy = categories['unexpected_fees']['amount_usd']
    total_impact = total_missing + total_fee_discrepancy

    # Category breakdown
    category_breakdown = {
        k: {
            'count': v['count'],
            'amount_usd': v['amount_usd'],
            'severity': v['severity'],
            'percentage': round(v['amount_usd'] / total_impact * 100, 1) if total_impact > 0 else 0
        }
        for k, v in categories.items()
    }

    # Top root causes
    root_causes = []
    if categories['missing_settlements']['amount_usd'] > 0:
        root_causes.append({
            'cause': 'Missing Settlements',
            'impact_usd': categories['missing_settlements']['amount_usd'],
            'description': f"{categories['missing_settlements']['count']} captured transactions have no settlement record"
        })

    if categories['unexpected_fees']['amount_usd'] > 0:
        root_causes.append({
            'cause': 'Unexpected Fees',
            'impact_usd': categories['unexpected_fees']['amount_usd'],
            'description': f"{categories['unexpected_fees']['count']} transactions with fee discrepancies"
        })

    if categories['timing_delays']['count'] > 0:
        root_causes.append({
            'cause': 'Settlement Delays',
            'impact_usd': categories['timing_delays']['amount_usd'],
            'description': f"{categories['timing_delays']['count']} settlements delayed beyond normal timeframe"
        })

    # Recommendations
    recommendations = [
        {
            'priority': 'Critical',
            'action': f"Immediately contact providers about {categories['missing_settlements']['count']} missing settlements worth ${categories['missing_settlements']['amount_usd']:,.2f} USD"
        },
        {
            'priority': 'High',
            'action': 'Review and renegotiate fee agreements with providers showing unexpected fee deductions'
        },
        {
            'priority': 'High',
            'action': 'Implement automated daily reconciliation to catch settlement gaps faster'
        },
        {
            'priority': 'Medium',
            'action': 'Establish SLAs with payment providers for settlement timing and investigate delays'
        },
        {
            'priority': 'Medium',
            'action': 'Set up alerts for transactions that exceed expected settlement windows'
        }
    ]

    insights = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'total_missing_revenue_usd': round(float(total_impact), 2),
            'total_transactions_analyzed': int(len(reconciled_df)),
            'critical_issues': categories['missing_settlements']['count'] + categories['unexpected_fees']['count'],
            'providers_analyzed': int(reconciled_df['provider'].nunique()),
            'countries_analyzed': int(reconciled_df['country'].nunique())
        },
        'category_breakdown': category_breakdown,
        'top_root_causes': sorted(root_causes, key=lambda x: x['impact_usd'], reverse=True)[:5],
        'provider_performance': metrics['by_provider'][:5],
        'payment_method_analysis': metrics['by_payment_method'],
        'country_analysis': metrics['by_country'],
        'patterns': patterns,
        'recommendations': recommendations
    }

    return insights


def analyze_revenue_anomalies():
    """
    Main analysis function that orchestrates the full analysis process.

    Process:
    1. Load reconciled data
    2. Calculate aggregate metrics
    3. Categorize missing revenue
    4. Identify patterns
    5. Generate prioritized anomalies
    6. Generate insights summary
    7. Save outputs to JSON files
    """
    print("=" * 60)
    print("Revenue Anomaly Analysis")
    print("=" * 60)
    print()

    # Step 1: Load reconciled data
    print("Step 1: Loading reconciled data...")
    reconciled_df = load_reconciled_data()
    print(f"Loaded {len(reconciled_df)} reconciled transactions")
    print()

    # Step 2: Calculate metrics
    print("Step 2: Calculating aggregate metrics...")
    metrics = calculate_aggregate_metrics(reconciled_df)
    print(f"Total discrepancy: ${metrics['overall']['total_discrepancy_usd']:,.2f} USD")
    print()

    # Step 3: Categorize revenue
    print("Step 3: Categorizing missing revenue...")
    categories = categorize_revenue(reconciled_df)
    print("Revenue Categories:")
    for category, data in categories.items():
        print(f"  {category}: ${data['amount_usd']:,.2f} USD ({data['count']} transactions)")
    print()

    # Step 4: Identify patterns
    print("Step 4: Identifying high-risk patterns...")
    patterns = identify_patterns(reconciled_df, categories)
    print(f"Identified {len(patterns)} key patterns")
    print()

    # Step 5: Generate anomalies
    print("Step 5: Generating prioritized anomaly list...")
    anomalies = generate_prioritized_anomalies(reconciled_df)
    print(f"Generated {len(anomalies)} prioritized anomalies")
    print()

    # Step 6: Generate insights
    print("Step 6: Generating insights summary...")
    insights = generate_insights_summary(metrics, categories, patterns, reconciled_df)
    print("✓ Insights summary generated")
    print()

    # Step 7: Save outputs
    print("Step 7: Saving analysis outputs...")
    Config.ensure_output_directory()

    insights_path = f"{Config.OUTPUT_PATH}insights.json"
    with open(insights_path, 'w') as f:
        json.dump(insights, f, indent=2)
    print(f"Insights saved to: {insights_path}")

    anomalies_path = f"{Config.OUTPUT_PATH}anomalies.json"
    with open(anomalies_path, 'w') as f:
        json.dump(anomalies, f, indent=2)
    print(f"Anomalies saved to: {anomalies_path}")

    print()
    print("=" * 60)
    print("✓ Analysis complete!")
    print("=" * 60)
    print()

    # Print summary
    print("Executive Summary:")
    print(f"  Total Missing Revenue: ${insights['summary']['total_missing_revenue_usd']:,.2f} USD")
    print(f"  Critical Issues: {insights['summary']['critical_issues']}")
    print()
    print("Top 3 Root Causes:")
    for i, cause in enumerate(insights['top_root_causes'][:3], 1):
        print(f"  {i}. {cause['cause']}: ${cause['impact_usd']:,.2f} USD")
        print(f"     {cause['description']}")
    print()

    return insights, anomalies


if __name__ == '__main__':
    analyze_revenue_anomalies()
