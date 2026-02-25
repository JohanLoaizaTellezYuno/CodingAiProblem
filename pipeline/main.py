"""
Main Pipeline Orchestrator

This module orchestrates the complete Horizon Gaming Revenue Anomaly Detector
pipeline, executing all stages from data generation through analysis.

Usage:
    python main.py                    # Run full pipeline
    python main.py --skip-generate    # Skip data generation
    python main.py --analyze-only     # Only run analysis
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Import pipeline modules
from generate_data import main as generate_data
from reconcile import reconcile_transactions, save_reconciled_data
from analyze import analyze_revenue_anomalies
from config import Config


def print_banner(title: str):
    """
    Print formatted banner for pipeline stages.

    Args:
        title: Stage title
    """
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def check_data_files_exist() -> bool:
    """
    Check if required data files exist.

    Returns:
        True if files exist, False otherwise
    """
    transactions_path = Path(Config.TRANSACTIONS_DATA_PATH)
    settlements_path = Path(Config.SETTLEMENTS_DATA_PATH)

    return transactions_path.exists() and settlements_path.exists()


def run_full_pipeline(skip_generate: bool = False):
    """
    Execute the complete revenue anomaly detection pipeline.

    Stages:
    1. Data Generation (optional)
    2. Settlement Reconciliation
    3. Revenue Anomaly Analysis

    Args:
        skip_generate: If True, skip data generation stage
    """
    start_time = datetime.now()

    print_banner("HORIZON GAMING REVENUE ANOMALY DETECTOR")
    print(f"Pipeline started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Stage 1: Data Generation
    if skip_generate:
        print_banner("STAGE 1: DATA GENERATION - SKIPPED")
        if not check_data_files_exist():
            print("ERROR: Data files not found and generation was skipped.")
            print("Please run without --skip-generate flag to generate test data.")
            sys.exit(1)
        print("Using existing data files.")
    else:
        print_banner("STAGE 1: DATA GENERATION")
        try:
            generate_data()
            print()
            print("✓ Stage 1 Complete: Test data generated successfully")
        except Exception as e:
            print(f"✗ Stage 1 Failed: {e}")
            sys.exit(1)

    # Stage 2: Settlement Reconciliation
    print_banner("STAGE 2: SETTLEMENT RECONCILIATION")
    try:
        reconciled_df, ghost_settlements = reconcile_transactions()
        save_reconciled_data(reconciled_df, ghost_settlements)
        print()
        print("✓ Stage 2 Complete: Reconciliation finished successfully")
    except Exception as e:
        print(f"✗ Stage 2 Failed: {e}")
        sys.exit(1)

    # Stage 3: Revenue Anomaly Analysis
    print_banner("STAGE 3: REVENUE ANOMALY ANALYSIS")
    try:
        insights, anomalies = analyze_revenue_anomalies()
        print("✓ Stage 3 Complete: Analysis finished successfully")
    except Exception as e:
        print(f"✗ Stage 3 Failed: {e}")
        sys.exit(1)

    # Pipeline Complete
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print_banner("PIPELINE EXECUTION COMPLETE")
    print(f"Started:  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration:.2f} seconds")
    print()
    print("Output Files:")
    print(f"  Transactions:        {Config.TRANSACTIONS_DATA_PATH}")
    print(f"  Settlements:         {Config.SETTLEMENTS_DATA_PATH}")
    print(f"  Reconciled Data:     {Config.OUTPUT_PATH}reconciled_data.csv")
    print(f"  Ghost Settlements:   {Config.OUTPUT_PATH}ghost_settlements.csv")
    print(f"  Insights:            {Config.OUTPUT_PATH}insights.json")
    print(f"  Anomalies:           {Config.OUTPUT_PATH}anomalies.json")
    print()
    print("Key Findings:")
    print(f"  Total Missing Revenue: ${insights['summary']['total_missing_revenue_usd']:,.2f} USD")
    print(f"  Critical Issues:       {insights['summary']['critical_issues']}")
    print(f"  Transactions Analyzed: {insights['summary']['total_transactions_analyzed']}")
    print()
    print("Next Steps:")
    print("  1. Review insights.json for detailed analysis")
    print("  2. Check anomalies.json for prioritized action items")
    print("  3. Launch dashboard to visualize findings:")
    print("     cd dashboard && npm run dev")
    print()
    print("=" * 70)


def run_analysis_only():
    """
    Run only the analysis stage (requires reconciled data to exist).
    """
    print_banner("HORIZON GAMING REVENUE ANOMALY DETECTOR - ANALYSIS ONLY")

    # Check if reconciled data exists
    reconciled_path = f"{Config.OUTPUT_PATH}reconciled_data.csv"
    if not Path(reconciled_path).exists():
        print(f"ERROR: Reconciled data not found at {reconciled_path}")
        print("Please run the full pipeline first: python main.py")
        sys.exit(1)

    print_banner("REVENUE ANOMALY ANALYSIS")
    try:
        insights, anomalies = analyze_revenue_anomalies()
        print("✓ Analysis Complete")
        print()
        print(f"Total Missing Revenue: ${insights['summary']['total_missing_revenue_usd']:,.2f} USD")
        print(f"Critical Issues: {insights['summary']['critical_issues']}")
    except Exception as e:
        print(f"✗ Analysis Failed: {e}")
        sys.exit(1)


def main():
    """
    Main entry point for pipeline execution.

    Parses command line arguments and executes appropriate pipeline stages.
    """
    parser = argparse.ArgumentParser(
        description='Horizon Gaming Revenue Anomaly Detector Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run full pipeline
  python main.py --skip-generate    # Skip data generation
  python main.py --analyze-only     # Only run analysis

For more information, see README.md
        """
    )

    parser.add_argument(
        '--skip-generate',
        action='store_true',
        help='Skip data generation stage (use existing data files)'
    )

    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Run only the analysis stage (requires reconciled data)'
    )

    args = parser.parse_args()

    # Execute pipeline based on arguments
    try:
        if args.analyze_only:
            run_analysis_only()
        else:
            run_full_pipeline(skip_generate=args.skip_generate)
    except KeyboardInterrupt:
        print()
        print("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"Pipeline failed with error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
