"""
Unit Tests for Fee Calculation Module

This module tests all fee calculation functions with various inputs including
edge cases, boundary conditions, and error scenarios.
"""

import pytest
import sys
from pathlib import Path

# Add pipeline directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'pipeline'))

from fees import (
    calculate_card_fee,
    calculate_bank_fee,
    calculate_voucher_fee,
    calculate_fee,
    calculate_expected_settlement,
    convert_to_usd
)
from config import Config


class TestCardFeeCalculation:
    """Tests for credit/debit card fee calculation."""

    def test_card_fee_standard_amount(self):
        """Test card fee calculation with standard amount."""
        # 2.9% + $0.30 on $100
        assert calculate_card_fee(100.0) == pytest.approx(3.20, rel=1e-2)

    def test_card_fee_small_amount(self):
        """Test card fee calculation with small amount."""
        # 2.9% + $0.30 on $10
        assert calculate_card_fee(10.0) == 0.59

    def test_card_fee_large_amount(self):
        """Test card fee calculation with large amount."""
        # 2.9% + $0.30 on $10,000
        assert calculate_card_fee(10000.0) == 290.30

    def test_card_fee_zero_amount(self):
        """Test card fee calculation with zero amount."""
        # Should still charge the fixed fee
        assert calculate_card_fee(0.0) == 0.30

    def test_card_fee_decimal_amount(self):
        """Test card fee calculation with decimal amount."""
        # 2.9% + $0.30 on $99.99
        expected = (99.99 * 0.029) + 0.30
        assert abs(calculate_card_fee(99.99) - expected) < 0.01

    def test_card_fee_boundary_values(self):
        """Test card fee with boundary values."""
        # Test very small positive amount
        assert calculate_card_fee(0.01) > 0.30

        # Test minimum typical transaction
        assert calculate_card_fee(1.0) == pytest.approx(0.329, rel=1e-2)


class TestBankFeeCalculation:
    """Tests for bank transfer fee calculation."""

    def test_bank_fee_standard_amount(self):
        """Test bank fee calculation with standard amount."""
        # 1.5% of $100
        assert calculate_bank_fee(100.0) == 1.5

    def test_bank_fee_large_amount(self):
        """Test bank fee calculation with large amount."""
        # 1.5% of $10,000
        assert calculate_bank_fee(10000.0) == 150.0

    def test_bank_fee_zero_amount(self):
        """Test bank fee calculation with zero amount."""
        assert calculate_bank_fee(0.0) == 0.0

    def test_bank_fee_decimal_amount(self):
        """Test bank fee calculation with decimal amount."""
        # 1.5% of $99.99
        expected = 99.99 * 0.015
        assert abs(calculate_bank_fee(99.99) - expected) < 0.01

    def test_bank_fee_small_amount(self):
        """Test bank fee with small amount."""
        assert calculate_bank_fee(10.0) == 0.15


class TestVoucherFeeCalculation:
    """Tests for cash voucher fee calculation."""

    def test_voucher_fee_standard_amount(self):
        """Test voucher fee calculation with standard amount."""
        # 3.5% of $100
        assert calculate_voucher_fee(100.0) == 3.5

    def test_voucher_fee_large_amount(self):
        """Test voucher fee calculation with large amount."""
        # 3.5% of $10,000
        assert calculate_voucher_fee(10000.0) == 350.0

    def test_voucher_fee_zero_amount(self):
        """Test voucher fee calculation with zero amount."""
        assert calculate_voucher_fee(0.0) == 0.0

    def test_voucher_fee_decimal_amount(self):
        """Test voucher fee calculation with decimal amount."""
        # 3.5% of $500.50
        expected = 500.50 * 0.035
        assert abs(calculate_voucher_fee(500.50) - expected) < 0.01


class TestCalculateFee:
    """Tests for the main fee calculation router function."""

    def test_fee_credit_card(self):
        """Test fee calculation for credit card."""
        result = calculate_fee(100.0, 'credit_card')
        expected = calculate_card_fee(100.0)
        assert result == expected

    def test_fee_debit_card(self):
        """Test fee calculation for debit card."""
        result = calculate_fee(100.0, 'debit_card')
        expected = calculate_card_fee(100.0)
        assert result == expected

    def test_fee_bank_transfer(self):
        """Test fee calculation for bank transfer."""
        result = calculate_fee(100.0, 'bank_transfer')
        expected = calculate_bank_fee(100.0)
        assert result == expected

    def test_fee_cash_voucher(self):
        """Test fee calculation for cash voucher."""
        result = calculate_fee(100.0, 'cash_voucher')
        expected = calculate_voucher_fee(100.0)
        assert result == expected

    def test_fee_unknown_method(self):
        """Test fee calculation with unknown payment method."""
        # Should default to card fee
        result = calculate_fee(100.0, 'unknown_method')
        expected = calculate_card_fee(100.0)
        assert result == expected

    def test_fee_case_sensitivity(self):
        """Test that payment method matching is case-sensitive."""
        # Lowercase should work
        result = calculate_fee(100.0, 'credit_card')
        assert result == calculate_card_fee(100.0)

    def test_fee_all_methods_different_amounts(self):
        """Test that different payment methods produce different fees."""
        amount = 1000.0
        card_fee = calculate_fee(amount, 'credit_card')
        bank_fee = calculate_fee(amount, 'bank_transfer')
        voucher_fee = calculate_fee(amount, 'cash_voucher')

        # All fees should be different
        assert card_fee != bank_fee
        assert bank_fee != voucher_fee
        assert card_fee != voucher_fee


class TestExpectedSettlement:
    """Tests for expected settlement amount calculation."""

    def test_expected_settlement_credit_card(self):
        """Test expected settlement for credit card."""
        amount = 100.0
        result = calculate_expected_settlement(amount, 'credit_card')
        fee = calculate_card_fee(amount)
        expected = amount - fee
        assert result == expected

    def test_expected_settlement_bank_transfer(self):
        """Test expected settlement for bank transfer."""
        amount = 1000.0
        result = calculate_expected_settlement(amount, 'bank_transfer')
        fee = calculate_bank_fee(amount)
        expected = amount - fee
        assert result == expected

    def test_expected_settlement_cash_voucher(self):
        """Test expected settlement for cash voucher."""
        amount = 500.0
        result = calculate_expected_settlement(amount, 'cash_voucher')
        fee = calculate_voucher_fee(amount)
        expected = amount - fee
        assert result == expected

    def test_expected_settlement_is_less_than_original(self):
        """Test that expected settlement is always less than original amount."""
        amount = 100.0
        methods = ['credit_card', 'debit_card', 'bank_transfer', 'cash_voucher']

        for method in methods:
            settlement = calculate_expected_settlement(amount, method)
            assert settlement < amount

    def test_expected_settlement_zero_amount(self):
        """Test expected settlement with zero amount."""
        # Credit card should have negative settlement due to fixed fee
        result = calculate_expected_settlement(0.0, 'credit_card')
        assert result == -0.30

        # Bank transfer should be zero
        result = calculate_expected_settlement(0.0, 'bank_transfer')
        assert result == 0.0


class TestCurrencyConversion:
    """Tests for currency conversion to USD."""

    def test_convert_brl_to_usd(self):
        """Test Brazilian Real to USD conversion."""
        result = convert_to_usd(100.0, 'BRL')
        expected = 100.0 * Config.BRL_TO_USD
        assert result == expected

    def test_convert_mxn_to_usd(self):
        """Test Mexican Peso to USD conversion."""
        result = convert_to_usd(100.0, 'MXN')
        expected = 100.0 * Config.MXN_TO_USD
        assert result == expected

    def test_convert_cop_to_usd(self):
        """Test Colombian Peso to USD conversion."""
        result = convert_to_usd(1000.0, 'COP')
        expected = 1000.0 * Config.COP_TO_USD
        assert result == expected

    def test_convert_clp_to_usd(self):
        """Test Chilean Peso to USD conversion."""
        result = convert_to_usd(1000.0, 'CLP')
        expected = 1000.0 * Config.CLP_TO_USD
        assert result == expected

    def test_convert_usd_to_usd(self):
        """Test USD to USD conversion (should be identity)."""
        result = convert_to_usd(100.0, 'USD')
        assert result == 100.0

    def test_convert_unknown_currency(self):
        """Test conversion with unknown currency."""
        # Should default to 1.0 rate (identity)
        result = convert_to_usd(100.0, 'EUR')
        assert result == 100.0

    def test_convert_zero_amount(self):
        """Test conversion with zero amount."""
        result = convert_to_usd(0.0, 'BRL')
        assert result == 0.0

    def test_convert_large_amounts(self):
        """Test conversion with large amounts."""
        # 1 million BRL to USD
        result = convert_to_usd(1000000.0, 'BRL')
        expected = 1000000.0 * Config.BRL_TO_USD
        assert result == expected

    def test_all_currencies_have_positive_rates(self):
        """Test that all defined currencies have positive exchange rates."""
        currencies = ['BRL', 'MXN', 'COP', 'CLP', 'USD']
        for currency in currencies:
            rate = Config.get_exchange_rate(currency)
            assert rate > 0


class TestFeeCalculationEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_large_transaction(self):
        """Test fee calculation with very large transaction."""
        amount = 1000000.0  # $1 million

        card_fee = calculate_card_fee(amount)
        assert card_fee == (amount * 0.029 + 0.30)

        bank_fee = calculate_bank_fee(amount)
        assert bank_fee == amount * 0.015

    def test_very_small_transaction(self):
        """Test fee calculation with very small transaction."""
        amount = 0.01  # $0.01

        card_fee = calculate_card_fee(amount)
        # Fixed fee dominates for small amounts
        assert card_fee > amount

    def test_fee_precision(self):
        """Test that fee calculations maintain precision."""
        amount = 123.456789

        card_fee = calculate_card_fee(amount)
        # Should have reasonable precision
        assert isinstance(card_fee, float)
        assert card_fee > 0

    def test_settlement_amount_precision(self):
        """Test that settlement amounts maintain precision."""
        amount = 99.99
        settlement = calculate_expected_settlement(amount, 'credit_card')

        # Should be precise to cents
        assert abs(settlement - round(settlement, 2)) < 0.01


# Parametrized tests for comprehensive coverage
class TestFeeCalculationParametrized:
    """Parametrized tests for comprehensive fee calculation testing."""

    @pytest.mark.parametrize("amount,expected", [
        (0, 0.30),
        (10, 0.59),
        (50, 1.75),
        (100, 3.20),
        (1000, 29.30),
    ])
    def test_card_fee_amounts(self, amount, expected):
        """Test card fees for various amounts."""
        assert calculate_card_fee(amount) == pytest.approx(expected, rel=1e-2)

    @pytest.mark.parametrize("amount,expected", [
        (0, 0.0),
        (100, 1.5),
        (1000, 15.0),
        (10000, 150.0),
    ])
    def test_bank_fee_amounts(self, amount, expected):
        """Test bank fees for various amounts."""
        assert calculate_bank_fee(amount) == expected

    @pytest.mark.parametrize("amount,expected", [
        (0, 0.0),
        (100, 3.5),
        (500, 17.5),
        (1000, 35.0),
    ])
    def test_voucher_fee_amounts(self, amount, expected):
        """Test voucher fees for various amounts."""
        assert calculate_voucher_fee(amount) == expected

    @pytest.mark.parametrize("method", [
        'credit_card',
        'debit_card',
        'bank_transfer',
        'cash_voucher'
    ])
    def test_all_payment_methods_return_positive_fee(self, method):
        """Test that all payment methods return positive fees for positive amounts."""
        amount = 100.0
        fee = calculate_fee(amount, method)
        assert fee > 0

    @pytest.mark.parametrize("currency,rate", [
        ('BRL', 0.20),
        ('MXN', 0.055),
        ('COP', 0.00025),
        ('CLP', 0.0011),
        ('USD', 1.0),
    ])
    def test_exchange_rates(self, currency, rate):
        """Test that exchange rates match configuration."""
        result = Config.get_exchange_rate(currency)
        assert result == rate


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
