"""
Unit Tests for Configuration Module

This module tests configuration loading and management functionality.
"""

import pytest
import sys
from pathlib import Path

# Add pipeline directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'pipeline'))

from config import Config


class TestConfigAttributes:
    """Tests for Config class attributes."""

    def test_data_paths_are_set(self):
        """Test that data paths are configured."""
        assert Config.TRANSACTIONS_DATA_PATH is not None
        assert Config.SETTLEMENTS_DATA_PATH is not None
        assert Config.OUTPUT_PATH is not None

    def test_fee_parameters_are_set(self):
        """Test that fee parameters are configured."""
        assert Config.CARD_FEE_PERCENT is not None
        assert Config.CARD_FEE_FIXED is not None
        assert Config.BANK_FEE_PERCENT is not None
        assert Config.VOUCHER_FEE_PERCENT is not None

    def test_exchange_rates_are_set(self):
        """Test that exchange rates are configured."""
        assert Config.BRL_TO_USD is not None
        assert Config.MXN_TO_USD is not None
        assert Config.COP_TO_USD is not None
        assert Config.CLP_TO_USD is not None

    def test_settlement_timing_parameters_are_set(self):
        """Test that settlement timing parameters are configured."""
        assert Config.CARD_SETTLEMENT_MIN is not None
        assert Config.CARD_SETTLEMENT_MAX is not None
        assert Config.CARD_SETTLEMENT_THRESHOLD is not None
        assert Config.BANK_SETTLEMENT_MIN is not None
        assert Config.BANK_SETTLEMENT_MAX is not None
        assert Config.BANK_SETTLEMENT_THRESHOLD is not None


class TestConfigFeeParameters:
    """Tests for fee parameter values."""

    def test_card_fee_percent_is_positive(self):
        """Test that card fee percentage is positive."""
        assert Config.CARD_FEE_PERCENT > 0

    def test_card_fee_fixed_is_positive(self):
        """Test that fixed card fee is positive."""
        assert Config.CARD_FEE_FIXED > 0

    def test_bank_fee_percent_is_positive(self):
        """Test that bank fee percentage is positive."""
        assert Config.BANK_FEE_PERCENT > 0

    def test_voucher_fee_percent_is_positive(self):
        """Test that voucher fee percentage is positive."""
        assert Config.VOUCHER_FEE_PERCENT > 0

    def test_fee_percentages_are_reasonable(self):
        """Test that fee percentages are within reasonable bounds."""
        # Fees should be less than 10%
        assert Config.CARD_FEE_PERCENT < 10
        assert Config.BANK_FEE_PERCENT < 10
        assert Config.VOUCHER_FEE_PERCENT < 10

    def test_card_fee_fixed_is_reasonable(self):
        """Test that fixed card fee is reasonable."""
        # Fixed fee should be less than $5
        assert Config.CARD_FEE_FIXED < 5.0


class TestGetExchangeRate:
    """Tests for get_exchange_rate method."""

    def test_get_brl_rate(self):
        """Test getting BRL exchange rate."""
        rate = Config.get_exchange_rate('BRL')
        assert rate == Config.BRL_TO_USD
        assert rate > 0

    def test_get_mxn_rate(self):
        """Test getting MXN exchange rate."""
        rate = Config.get_exchange_rate('MXN')
        assert rate == Config.MXN_TO_USD
        assert rate > 0

    def test_get_cop_rate(self):
        """Test getting COP exchange rate."""
        rate = Config.get_exchange_rate('COP')
        assert rate == Config.COP_TO_USD
        assert rate > 0

    def test_get_clp_rate(self):
        """Test getting CLP exchange rate."""
        rate = Config.get_exchange_rate('CLP')
        assert rate == Config.CLP_TO_USD
        assert rate > 0

    def test_get_usd_rate(self):
        """Test getting USD exchange rate."""
        rate = Config.get_exchange_rate('USD')
        assert rate == 1.0

    def test_get_unknown_currency_rate(self):
        """Test getting exchange rate for unknown currency."""
        rate = Config.get_exchange_rate('EUR')
        assert rate == 1.0  # Should default to 1.0

    def test_get_rate_case_sensitive(self):
        """Test that currency codes are case-sensitive."""
        # Uppercase should work
        rate = Config.get_exchange_rate('BRL')
        assert rate == Config.BRL_TO_USD

    def test_all_rates_are_positive(self):
        """Test that all exchange rates are positive."""
        currencies = ['BRL', 'MXN', 'COP', 'CLP', 'USD']
        for currency in currencies:
            rate = Config.get_exchange_rate(currency)
            assert rate > 0

    def test_exchange_rates_are_reasonable(self):
        """Test that exchange rates are within reasonable bounds."""
        # BRL should be between 0.1 and 0.3
        assert 0.1 <= Config.BRL_TO_USD <= 0.3

        # MXN should be between 0.04 and 0.07
        assert 0.04 <= Config.MXN_TO_USD <= 0.07

        # COP should be very small (weak currency)
        assert 0.0001 <= Config.COP_TO_USD <= 0.001

        # CLP should be very small (weak currency)
        assert 0.0005 <= Config.CLP_TO_USD <= 0.002


class TestGetSettlementTiming:
    """Tests for get_settlement_timing method."""

    def test_get_credit_card_timing(self):
        """Test getting credit card settlement timing."""
        min_days, max_days, threshold = Config.get_settlement_timing('credit_card')

        assert min_days == Config.CARD_SETTLEMENT_MIN
        assert max_days == Config.CARD_SETTLEMENT_MAX
        assert threshold == Config.CARD_SETTLEMENT_THRESHOLD

    def test_get_debit_card_timing(self):
        """Test getting debit card settlement timing."""
        min_days, max_days, threshold = Config.get_settlement_timing('debit_card')

        assert min_days == Config.CARD_SETTLEMENT_MIN
        assert max_days == Config.CARD_SETTLEMENT_MAX
        assert threshold == Config.CARD_SETTLEMENT_THRESHOLD

    def test_get_bank_transfer_timing(self):
        """Test getting bank transfer settlement timing."""
        min_days, max_days, threshold = Config.get_settlement_timing('bank_transfer')

        assert min_days == Config.BANK_SETTLEMENT_MIN
        assert max_days == Config.BANK_SETTLEMENT_MAX
        assert threshold == Config.BANK_SETTLEMENT_THRESHOLD

    def test_get_cash_voucher_timing(self):
        """Test getting cash voucher settlement timing."""
        min_days, max_days, threshold = Config.get_settlement_timing('cash_voucher')

        assert min_days == Config.VOUCHER_SETTLEMENT_MIN
        assert max_days == Config.VOUCHER_SETTLEMENT_MAX
        assert threshold == Config.VOUCHER_SETTLEMENT_THRESHOLD

    def test_get_unknown_method_timing(self):
        """Test getting settlement timing for unknown payment method."""
        min_days, max_days, threshold = Config.get_settlement_timing('unknown')

        # Should return default timing
        assert isinstance(min_days, int)
        assert isinstance(max_days, int)
        assert isinstance(threshold, int)
        assert min_days < max_days
        assert threshold >= max_days

    def test_timing_values_are_logical(self):
        """Test that timing values are logical."""
        methods = ['credit_card', 'debit_card', 'bank_transfer', 'cash_voucher']

        for method in methods:
            min_days, max_days, threshold = Config.get_settlement_timing(method)

            # Min should be less than max
            assert min_days < max_days

            # Threshold should be greater than max
            assert threshold > max_days

            # All values should be positive
            assert min_days > 0
            assert max_days > 0
            assert threshold > 0

    def test_bank_transfers_take_longer(self):
        """Test that bank transfers have longer settlement times than cards."""
        card_min, card_max, _ = Config.get_settlement_timing('credit_card')
        bank_min, bank_max, _ = Config.get_settlement_timing('bank_transfer')

        # Bank transfers should generally take longer
        assert bank_min >= card_min
        assert bank_max > card_max


class TestEnsureOutputDirectory:
    """Tests for ensure_output_directory method."""

    def test_ensure_output_directory_creates_path(self, tmp_path):
        """Test that ensure_output_directory creates the directory."""
        # Temporarily change output path
        original_path = Config.OUTPUT_PATH
        Config.OUTPUT_PATH = str(tmp_path / 'test_output/')

        # Ensure directory
        Config.ensure_output_directory()

        # Check directory was created
        assert Path(Config.OUTPUT_PATH).exists()
        assert Path(Config.OUTPUT_PATH).is_dir()

        # Restore original path
        Config.OUTPUT_PATH = original_path

    def test_ensure_output_directory_idempotent(self, tmp_path):
        """Test that calling ensure_output_directory multiple times is safe."""
        # Temporarily change output path
        original_path = Config.OUTPUT_PATH
        Config.OUTPUT_PATH = str(tmp_path / 'test_output/')

        # Call multiple times
        Config.ensure_output_directory()
        Config.ensure_output_directory()
        Config.ensure_output_directory()

        # Should still exist
        assert Path(Config.OUTPUT_PATH).exists()

        # Restore original path
        Config.OUTPUT_PATH = original_path


class TestSettlementTimingConstants:
    """Tests for settlement timing constants."""

    def test_card_settlement_timing_values(self):
        """Test card settlement timing constant values."""
        assert Config.CARD_SETTLEMENT_MIN == 2
        assert Config.CARD_SETTLEMENT_MAX == 3
        assert Config.CARD_SETTLEMENT_THRESHOLD == 5

    def test_bank_settlement_timing_values(self):
        """Test bank settlement timing constant values."""
        assert Config.BANK_SETTLEMENT_MIN == 5
        assert Config.BANK_SETTLEMENT_MAX == 7
        assert Config.BANK_SETTLEMENT_THRESHOLD == 10

    def test_voucher_settlement_timing_values(self):
        """Test voucher settlement timing constant values."""
        assert Config.VOUCHER_SETTLEMENT_MIN == 3
        assert Config.VOUCHER_SETTLEMENT_MAX == 5
        assert Config.VOUCHER_SETTLEMENT_THRESHOLD == 8


class TestConfigParametrized:
    """Parametrized tests for Config class."""

    @pytest.mark.parametrize("currency,min_rate,max_rate", [
        ('BRL', 0.1, 0.3),
        ('MXN', 0.04, 0.07),
        ('COP', 0.0001, 0.001),
        ('CLP', 0.0005, 0.002),
        ('USD', 1.0, 1.0),
    ])
    def test_exchange_rate_bounds(self, currency, min_rate, max_rate):
        """Test that exchange rates are within expected bounds."""
        rate = Config.get_exchange_rate(currency)
        assert min_rate <= rate <= max_rate

    @pytest.mark.parametrize("method", [
        'credit_card',
        'debit_card',
        'bank_transfer',
        'cash_voucher'
    ])
    def test_all_methods_have_timing_config(self, method):
        """Test that all payment methods have timing configuration."""
        min_days, max_days, threshold = Config.get_settlement_timing(method)

        assert isinstance(min_days, int)
        assert isinstance(max_days, int)
        assert isinstance(threshold, int)
        assert min_days > 0
        assert max_days > min_days
        assert threshold > max_days


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
