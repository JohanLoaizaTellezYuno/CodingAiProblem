"""
Fee Calculation Module

This module implements fee calculation logic for different payment methods
used by Horizon Gaming across Latin American payment providers.

Fee Structure:
- Credit/Debit Cards: 2.9% + $0.30 per transaction
- Bank Transfers: 1.5% of transaction amount
- Cash Vouchers: 3.5% of transaction amount
"""

from config import Config


def calculate_card_fee(amount: float) -> float:
    """
    Calculate processing fee for credit card or debit card transactions.

    Fee structure: 2.9% + $0.30

    Args:
        amount: Transaction amount in original currency

    Returns:
        Processing fee amount

    Examples:
        >>> calculate_card_fee(100.0)
        3.2
        >>> calculate_card_fee(50.0)
        1.75
    """
    return (amount * Config.CARD_FEE_PERCENT / 100) + Config.CARD_FEE_FIXED


def calculate_bank_fee(amount: float) -> float:
    """
    Calculate processing fee for bank transfer transactions.

    Fee structure: 1.5% of amount

    Args:
        amount: Transaction amount in original currency

    Returns:
        Processing fee amount

    Examples:
        >>> calculate_bank_fee(100.0)
        1.5
        >>> calculate_bank_fee(1000.0)
        15.0
    """
    return amount * Config.BANK_FEE_PERCENT / 100


def calculate_voucher_fee(amount: float) -> float:
    """
    Calculate processing fee for cash voucher transactions.

    Fee structure: 3.5% of amount

    Args:
        amount: Transaction amount in original currency

    Returns:
        Processing fee amount

    Examples:
        >>> calculate_voucher_fee(100.0)
        3.5
        >>> calculate_voucher_fee(500.0)
        17.5
    """
    return amount * Config.VOUCHER_FEE_PERCENT / 100


def calculate_fee(amount: float, payment_method: str) -> float:
    """
    Calculate processing fee based on payment method.

    This is the main entry point for fee calculation. It routes to the
    appropriate calculation function based on payment method.

    Args:
        amount: Transaction amount in original currency
        payment_method: Payment method type (credit_card, debit_card,
                       bank_transfer, cash_voucher)

    Returns:
        Processing fee amount

    Examples:
        >>> calculate_fee(100.0, 'credit_card')
        3.2
        >>> calculate_fee(100.0, 'bank_transfer')
        1.5
        >>> calculate_fee(100.0, 'cash_voucher')
        3.5
    """
    if payment_method in ['credit_card', 'debit_card']:
        return calculate_card_fee(amount)
    elif payment_method == 'bank_transfer':
        return calculate_bank_fee(amount)
    elif payment_method == 'cash_voucher':
        return calculate_voucher_fee(amount)
    else:
        # Default to card fee for unknown methods
        return calculate_card_fee(amount)


def calculate_expected_settlement(amount: float, payment_method: str) -> float:
    """
    Calculate expected settlement amount after fees are deducted.

    Args:
        amount: Transaction amount in original currency
        payment_method: Payment method type

    Returns:
        Expected settlement amount (transaction amount - fees)

    Examples:
        >>> calculate_expected_settlement(100.0, 'credit_card')
        96.8
        >>> calculate_expected_settlement(100.0, 'bank_transfer')
        98.5
    """
    fee = calculate_fee(amount, payment_method)
    return amount - fee


def convert_to_usd(amount: float, currency: str) -> float:
    """
    Convert amount from local currency to USD.

    Args:
        amount: Amount in local currency
        currency: ISO currency code (BRL, MXN, COP, CLP)

    Returns:
        Amount in USD

    Examples:
        >>> convert_to_usd(100.0, 'BRL')
        20.0
        >>> convert_to_usd(1000.0, 'MXN')
        55.0
    """
    rate = Config.get_exchange_rate(currency)
    return amount * rate
