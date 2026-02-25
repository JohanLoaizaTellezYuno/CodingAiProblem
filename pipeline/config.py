"""
Configuration Management Module

This module loads environment variables and provides centralized configuration
for the Horizon Gaming Revenue Anomaly Detector pipeline.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Central configuration class for pipeline parameters.

    Attributes:
        TRANSACTIONS_DATA_PATH: Path to transactions CSV file
        SETTLEMENTS_DATA_PATH: Path to settlements CSV file
        OUTPUT_PATH: Path to output directory for processed files
        CARD_FEE_PERCENT: Credit/debit card processing fee percentage
        CARD_FEE_FIXED: Fixed fee per card transaction
        BANK_FEE_PERCENT: Bank transfer processing fee percentage
        VOUCHER_FEE_PERCENT: Cash voucher processing fee percentage
        BRL_TO_USD: Brazilian Real to USD exchange rate
        MXN_TO_USD: Mexican Peso to USD exchange rate
        COP_TO_USD: Colombian Peso to USD exchange rate
        CLP_TO_USD: Chilean Peso to USD exchange rate
    """

    # Data paths
    TRANSACTIONS_DATA_PATH = os.getenv('TRANSACTIONS_DATA_PATH', './data/raw/transactions.csv')
    SETTLEMENTS_DATA_PATH = os.getenv('SETTLEMENTS_DATA_PATH', './data/raw/settlements.csv')
    OUTPUT_PATH = os.getenv('OUTPUT_PATH', './data/processed/')

    # Fee parameters
    CARD_FEE_PERCENT = float(os.getenv('CARD_FEE_PERCENT', 2.9))
    CARD_FEE_FIXED = float(os.getenv('CARD_FEE_FIXED', 0.30))
    BANK_FEE_PERCENT = float(os.getenv('BANK_FEE_PERCENT', 1.5))
    VOUCHER_FEE_PERCENT = float(os.getenv('VOUCHER_FEE_PERCENT', 3.5))

    # Currency exchange rates to USD
    BRL_TO_USD = float(os.getenv('BRL_TO_USD', 0.20))
    MXN_TO_USD = float(os.getenv('MXN_TO_USD', 0.055))
    COP_TO_USD = float(os.getenv('COP_TO_USD', 0.00025))
    CLP_TO_USD = float(os.getenv('CLP_TO_USD', 0.0011))

    # Settlement timing norms (in days)
    CARD_SETTLEMENT_MIN = 2
    CARD_SETTLEMENT_MAX = 3
    CARD_SETTLEMENT_THRESHOLD = 5  # Flag if exceeds this

    BANK_SETTLEMENT_MIN = 5
    BANK_SETTLEMENT_MAX = 7
    BANK_SETTLEMENT_THRESHOLD = 10

    VOUCHER_SETTLEMENT_MIN = 3
    VOUCHER_SETTLEMENT_MAX = 5
    VOUCHER_SETTLEMENT_THRESHOLD = 8

    @classmethod
    def get_exchange_rate(cls, currency: str) -> float:
        """
        Get exchange rate for a given currency.

        Args:
            currency: ISO currency code (BRL, MXN, COP, CLP)

        Returns:
            Exchange rate to USD
        """
        rates = {
            'BRL': cls.BRL_TO_USD,
            'MXN': cls.MXN_TO_USD,
            'COP': cls.COP_TO_USD,
            'CLP': cls.CLP_TO_USD,
            'USD': 1.0
        }
        return rates.get(currency, 1.0)

    @classmethod
    def get_settlement_timing(cls, payment_method: str) -> tuple:
        """
        Get expected settlement timing for a payment method.

        Args:
            payment_method: Payment method type

        Returns:
            Tuple of (min_days, max_days, threshold_days)
        """
        timing = {
            'credit_card': (cls.CARD_SETTLEMENT_MIN, cls.CARD_SETTLEMENT_MAX, cls.CARD_SETTLEMENT_THRESHOLD),
            'debit_card': (cls.CARD_SETTLEMENT_MIN, cls.CARD_SETTLEMENT_MAX, cls.CARD_SETTLEMENT_THRESHOLD),
            'bank_transfer': (cls.BANK_SETTLEMENT_MIN, cls.BANK_SETTLEMENT_MAX, cls.BANK_SETTLEMENT_THRESHOLD),
            'cash_voucher': (cls.VOUCHER_SETTLEMENT_MIN, cls.VOUCHER_SETTLEMENT_MAX, cls.VOUCHER_SETTLEMENT_THRESHOLD)
        }
        return timing.get(payment_method, (2, 5, 7))

    @classmethod
    def ensure_output_directory(cls):
        """Create output directory if it doesn't exist."""
        Path(cls.OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
