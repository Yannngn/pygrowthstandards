from decimal import Decimal as D

import numpy as np
import pytest

from src.utils.decimal_stats import (
    Number,
    calculate_z_score,
    estimate_lms_from_sd,
    normal_cdf,
)


class TestDecimalStats:
    """Test suite for decimal_stats utility functions."""

    def test_number_type_alias(self):
        """Test that Number type alias works correctly."""
        # Test with Decimal
        decimal_val: Number = D("1.5")
        assert isinstance(decimal_val, D)

        # Test with float
        float_val: Number = 1.5
        assert isinstance(float_val, float)

    def test_normal_cdf_with_decimal(self):
        """Test normal CDF with Decimal input."""
        # Test z-score of 0 (should be 0.5)
        result = normal_cdf(D("0.0"))
        assert isinstance(result, D)
        assert abs(result - D("0.5")) < D("0.001")

        # Test z-score of 1 (should be approximately 0.8413)
        result = normal_cdf(D("1.0"))
        assert isinstance(result, D)
        assert abs(result - D("0.8413")) < D("0.001")

        # Test z-score of -1 (should be approximately 0.1587)
        result = normal_cdf(D("-1.0"))
        assert isinstance(result, D)
        assert abs(result - D("0.1587")) < D("0.001")

    def test_normal_cdf_with_float(self):
        """Test normal CDF with float input."""
        # Test z-score of 0 (should be 0.5)
        result = normal_cdf(0.0)
        assert isinstance(result, D)
        assert abs(result - D("0.5")) < D("0.001")

        # Test z-score of 2 (should be approximately 0.9772)
        result = normal_cdf(2.0)
        assert isinstance(result, D)
        assert abs(result - D("0.9772")) < D("0.001")

    def test_normal_cdf_extreme_values(self):
        """Test normal CDF with extreme values."""
        # Very negative z-score
        result = normal_cdf(D("-5.0"))
        assert result < D("0.001")

        # Very positive z-score
        result = normal_cdf(D("5.0"))
        assert result > D("0.999")

    def test_calculate_z_score_lambda_zero_decimal(self):
        """Test z-score calculation when lambda is zero with Decimal inputs."""
        value = D("110.0")
        lamb = D("0.0")
        mu = D("100.0")
        sigma = D("0.1")

        # When lambda = 0: z_score = (value/mu - 1) / sigma
        expected = (value / mu - 1) / sigma
        result = calculate_z_score(value, lamb, mu, sigma)

        assert isinstance(result, D)
        assert abs(result - expected) < D("0.001")

    def test_calculate_z_score_lambda_zero_mixed_types(self):
        """Test z-score calculation when lambda is zero with mixed types."""
        value = 110.0  # float
        lamb = D("0.0")  # Decimal
        mu = 100.0  # float
        sigma = D("0.1")  # Decimal

        # When lambda = 0: z_score = (value/mu - 1) / sigma
        expected = (D("110.0") / D("100.0") - 1) / D("0.1")
        result = calculate_z_score(value, lamb, mu, sigma)

        assert isinstance(result, D)
        assert abs(result - expected) < D("0.001")

    def test_calculate_z_score_lambda_nonzero_decimal(self):
        """Test z-score calculation when lambda is non-zero with Decimal inputs."""
        value = D("110.0")
        lamb = D("0.5")
        mu = D("100.0")
        sigma = D("0.1")

        # When lambda != 0: z_score = ((value/mu)^lambda - 1) / (lambda * sigma)
        expected = ((value / mu) ** lamb - 1) / (lamb * sigma)
        result = calculate_z_score(value, lamb, mu, sigma)

        assert isinstance(result, D)
        assert abs(result - expected) < D("0.001")

    def test_calculate_z_score_lambda_nonzero_mixed_types(self):
        """Test z-score calculation when lambda is non-zero with mixed types."""
        value = 110.0  # float
        lamb = 0.3  # float
        mu = D("100.0")  # Decimal
        sigma = 0.1  # float

        # Should convert all to Decimal internally
        result = calculate_z_score(value, lamb, mu, sigma)

        assert isinstance(result, D)
        # Should be a reasonable z-score
        assert D("-5.0") < result < D("5.0")

    def test_calculate_z_score_precision(self):
        """Test z-score calculation precision with Decimal."""
        value = D("100.5")
        lamb = D("0.0")
        mu = D("100.0")
        sigma = D("0.1")

        result = calculate_z_score(value, lamb, mu, sigma)

        # Should maintain high precision
        expected = D("0.05")  # (100.5/100.0 - 1) / 0.1 = 0.05
        assert abs(result - expected) < D("0.0001")

    def test_calculate_z_score_edge_cases(self):
        """Test z-score calculation edge cases."""
        # Test with value equal to mu (should give z-score of 0)
        value = D("100.0")
        lamb = D("0.0")
        mu = D("100.0")
        sigma = D("0.1")

        result = calculate_z_score(value, lamb, mu, sigma)
        assert abs(result - D("0.0")) < D("0.0001")

        # Test with very small sigma
        sigma_small = D("0.001")
        result = calculate_z_score(D("100.1"), lamb, mu, sigma_small)
        assert abs(result - D("1.0")) < D("1.0")

    def test_estimate_lms_from_sd_no_zero(self):
        """Test LMS estimation when z-scores don't contain zero."""
        z_scores = np.array([-2, -1, 1, 2])
        values = np.array([95, 98, 105, 110])

        with pytest.raises(ValueError, match="z_scores must contain a zero value"):
            estimate_lms_from_sd(z_scores, values)

    def test_estimate_lms_from_sd_with_zero(self):
        """Test LMS estimation when z-scores contain zero."""
        z_scores = np.array([-2, -1, 0, 1, 2])
        values = np.array([90, 95, 100, 105, 110])

        try:
            result = estimate_lms_from_sd(z_scores, values)

            # Should return tuple of 3 Decimal values
            assert isinstance(result, tuple)
            assert len(result) == 3

            L, M, S = result
            assert isinstance(L, D)
            assert isinstance(M, D)
            assert isinstance(S, D)

            # M should be close to the value at z=0
            assert abs(M - D("100.0")) < D("1.0")

        except ImportError:
            # curve_fit might not be available in all environments
            pytest.skip("scipy.optimize.curve_fit not available")

    def test_estimate_lms_from_sd_realistic_data(self):
        """Test LMS estimation with realistic growth data."""
        # Create realistic growth data
        z_scores = np.array([-2, -1, 0, 1, 2])
        # Height data for 1-year-old (approximate)
        heights = np.array([69, 72, 75, 78, 81])  # cm

        try:
            L, M, S = estimate_lms_from_sd(z_scores, heights)

            # Check that parameters are reasonable
            assert isinstance(L, D)
            assert isinstance(M, D)
            assert isinstance(S, D)

            # L should be small (close to 0 for normal-like distribution)
            assert abs(L) < D("2.0")

            # M should be close to the median value
            assert abs(M - D("75.0")) < D("5.0")

            # S should be positive and reasonable
            assert D("0.01") < S < D("1.0")

        except ImportError:
            # curve_fit might not be available in all environments
            pytest.skip("scipy.optimize.curve_fit not available")

    def test_type_conversion_consistency(self):
        """Test that type conversions are consistent."""
        # Test that float inputs are properly converted to Decimal
        float_val = 1.5
        decimal_val = D("1.5")

        # Both should give same result in normal_cdf
        result_float = normal_cdf(float_val)
        result_decimal = normal_cdf(decimal_val)

        assert abs(result_float - result_decimal) < D("0.000001")

        # Both should give same result in calculate_z_score
        result_float = calculate_z_score(110.0, 0.0, 100.0, 0.1)
        result_decimal = calculate_z_score(D("110.0"), D("0.0"), D("100.0"), D("0.1"))

        assert abs(result_float - result_decimal) < D("0.000001")

    def test_decimal_precision_preservation(self):
        """Test that Decimal precision is preserved in calculations."""
        # Use high precision Decimal values
        value = D("110.123456789")
        lamb = D("0.0")
        mu = D("100.0")
        sigma = D("0.1")

        result = calculate_z_score(value, lamb, mu, sigma)

        # Should maintain precision
        expected = (D("110.123456789") / D("100.0") - 1) / D("0.1")
        assert abs(result - expected) < D("0.0000000001")

    '''    def test_rounding_behavior(self):
            """Test rounding behavior in normal_cdf."""
            # Test that normal_cdf rounds to 6 decimal places
            result = normal_cdf(D("0.123456789"))

            # Result should be rounded to 6 decimal places
            str_result = str(result)
            print(str_result)
            if "." in str_result:
                decimal_places = len(str_result.split(".")[1])
                assert decimal_places <= 6
    '''

    def test_special_values(self):
        """Test handling of special values."""
        # Test with very small values
        small_val = D("0.000001")
        result = normal_cdf(small_val)
        assert D("0.4") < result < D("0.6")  # Should be close to 0.5

        # Test with very large values (but not infinite)
        large_val = D("10.0")
        result = normal_cdf(large_val)
        assert result > D("0.99999")

    def test_negative_values(self):
        """Test handling of negative values."""
        # Test z-score calculation with negative values
        value = D("90.0")  # Below mean
        lamb = D("0.0")
        mu = D("100.0")
        sigma = D("0.1")

        result = calculate_z_score(value, lamb, mu, sigma)
        assert result < D("0.0")  # Should be negative

        # Test normal_cdf with negative z-score
        cdf_result = normal_cdf(result)
        assert D("0.0") < cdf_result < D("0.5")  # Should be less than 0.5
        assert D("0.0") < cdf_result < D("0.5")  # Should be less than 0.5
