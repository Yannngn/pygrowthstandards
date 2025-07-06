import numpy as np
import pytest

from src.utils.stats import (
    calculate_value_for_z_score,
    calculate_z_score,
    estimate_lms_from_sd,
    interpolate_array,
    interpolate_lms,
    normal_cdf,
)


class TestStats:
    """Test suite for stats utility functions."""

    def test_normal_cdf_standard_values(self):
        """Test normal CDF with standard values."""
        # Test z-score of 0 (should be 0.5)
        assert abs(normal_cdf(0.0) - 0.5) < 0.001

        # Test z-score of 1 (should be approximately 0.8413)
        assert abs(normal_cdf(1.0) - 0.8413) < 0.001

        # Test z-score of -1 (should be approximately 0.1587)
        assert abs(normal_cdf(-1.0) - 0.1587) < 0.001

        # Test z-score of 2 (should be approximately 0.9772)
        assert abs(normal_cdf(2.0) - 0.9772) < 0.001

    def test_normal_cdf_extreme_values(self):
        """Test normal CDF with extreme values."""
        # Very negative z-score
        assert normal_cdf(-5.0) < 0.001

        # Very positive z-score
        assert normal_cdf(5.0) > 0.999

    def test_calculate_value_for_z_score_lambda_zero(self):
        """Test value calculation when lambda is zero."""
        z_score = 1.0
        lamb = 0.0
        mu = 100.0
        sigma = 0.1

        # When lambda = 0: value = mu * (1 + sigma * z_score)
        expected = mu * (1 + sigma * z_score)
        result = calculate_value_for_z_score(z_score, lamb, mu, sigma)

        assert abs(result - expected) < 0.001

    def test_calculate_value_for_z_score_lambda_nonzero(self):
        """Test value calculation when lambda is non-zero."""
        z_score = 1.0
        lamb = 0.5
        mu = 100.0
        sigma = 0.1

        # When lambda != 0: value = mu * (1 + lambda * sigma * z_score)^(1/lambda)
        expected = mu * np.power(1 + lamb * sigma * z_score, 1 / lamb)
        result = calculate_value_for_z_score(z_score, lamb, mu, sigma)

        assert abs(result - expected) < 0.001

    def test_calculate_z_score_lambda_zero(self):
        """Test z-score calculation when lambda is zero."""
        value = 110.0
        lamb = 0.0
        mu = 100.0
        sigma = 0.1

        # When lambda = 0: z_score = (value/mu - 1) / sigma
        expected = (value / mu - 1) / sigma
        result = calculate_z_score(value, lamb, mu, sigma)

        assert abs(result - expected) < 0.001

    def test_calculate_z_score_lambda_nonzero(self):
        """Test z-score calculation when lambda is non-zero."""
        value = 110.0
        lamb = 0.5
        mu = 100.0
        sigma = 0.1

        # When lambda != 0: z_score = ((value/mu)^lambda - 1) / (lambda * sigma)
        expected = ((value / mu) ** lamb - 1) / (lamb * sigma)
        result = calculate_z_score(value, lamb, mu, sigma)

        assert abs(result - expected) < 0.001

    def test_calculate_value_and_z_score_roundtrip(self):
        """Test that value and z-score calculations are inverse operations."""
        # Test with lambda = 0
        z_score = 1.5
        lamb = 0.0
        mu = 100.0
        sigma = 0.1

        value = calculate_value_for_z_score(z_score, lamb, mu, sigma)
        recovered_z = calculate_z_score(value, lamb, mu, sigma)

        assert abs(recovered_z - z_score) < 0.001

        # Test with lambda != 0
        lamb = 0.3
        value = calculate_value_for_z_score(z_score, lamb, mu, sigma)
        recovered_z = calculate_z_score(value, lamb, mu, sigma)

        assert abs(recovered_z - z_score) < 0.001

    def test_estimate_lms_from_sd_basic(self):
        """Test LMS estimation from standard deviation data."""
        # Create test data with known LMS parameters
        z_scores = np.array([-2, -1, 0, 1, 2])
        lamb = 0.2
        mu = 100.0
        sigma = 0.15

        # Generate values using known LMS parameters
        values = np.array([calculate_value_for_z_score(z, lamb, mu, sigma) for z in z_scores])

        # Estimate LMS parameters
        estimated_l, estimated_m, estimated_s = estimate_lms_from_sd(z_scores, values)

        # Check that estimates are reasonably close to original values
        assert abs(estimated_l - lamb) < 0.1
        assert abs(estimated_m - mu) < 1.0
        assert abs(estimated_s - sigma) < 0.05

    def test_estimate_lms_from_sd_no_zero(self):
        """Test LMS estimation when z-scores don't contain zero."""
        z_scores = np.array([-2, -1, 1, 2])
        values = np.array([95, 98, 105, 110])

        with pytest.raises(ValueError, match="z_scores must contain a zero value"):
            estimate_lms_from_sd(z_scores, values)

    def test_interpolate_array_basic(self):
        """Test basic array interpolation."""
        x_values = np.array([0, 1, 2, 3, 4])
        y_values = np.array([0, 10, 20, 30, 40])

        # Test interpolation at known points
        assert interpolate_array(x_values, y_values, 0) == 0
        assert interpolate_array(x_values, y_values, 2) == 20

        # Test interpolation between points
        result = interpolate_array(x_values, y_values, 1.5)
        assert 10 < result < 20

    def test_interpolate_array_with_n_points(self):
        """Test array interpolation with specified number of points."""
        x_values = np.array([0, 1, 2, 3, 4, 5])
        y_values = np.array([0, 10, 20, 30, 40, 50])

        # Test with different numbers of points
        result_2 = interpolate_array(x_values, y_values, 2.5, n_points=2)
        result_4 = interpolate_array(x_values, y_values, 2.5, n_points=4)

        # Both should be reasonable interpolations
        assert 20 < result_2 < 30
        assert 20 < result_4 < 30

    def test_interpolate_array_all_points(self):
        """Test array interpolation using all points."""
        x_values = np.array([0, 1, 2, 3, 4])
        y_values = np.array([0, 10, 20, 30, 40])

        # Test with n_points = -1 (use all points)
        result = interpolate_array(x_values, y_values, 2.5, n_points=-1)
        assert 20 < result < 30

    def test_interpolate_lms_basic(self):
        """Test LMS interpolation."""
        x_values = np.array([0, 1, 2, 3, 4])
        l_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        m_values = np.array([100, 110, 120, 130, 140])
        s_values = np.array([0.1, 0.12, 0.14, 0.16, 0.18])

        # Test interpolation at known points
        l, m, s = interpolate_lms(x_values, l_values, m_values, s_values, 2)
        assert abs(l - 0.3) < 0.001
        assert abs(m - 120) < 0.001
        assert abs(s - 0.14) < 0.001

        # Test interpolation between points
        l, m, s = interpolate_lms(x_values, l_values, m_values, s_values, 1.5)
        assert 0.2 < l < 0.3
        assert 110 < m < 120
        assert 0.12 < s < 0.14

    def test_interpolate_lms_out_of_bounds(self):
        """Test LMS interpolation with out-of-bounds values."""
        x_values = np.array([0, 1, 2, 3, 4])
        l_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        m_values = np.array([100, 110, 120, 130, 140])
        s_values = np.array([0.1, 0.12, 0.14, 0.16, 0.18])

        # Test with value below range
        with pytest.raises(ValueError, match="x -1 is out of bounds"):
            interpolate_lms(x_values, l_values, m_values, s_values, -1)

        # Test with value above range
        with pytest.raises(ValueError, match="x 5 is out of bounds"):
            interpolate_lms(x_values, l_values, m_values, s_values, 5)

    def test_interpolate_lms_with_n_points(self):
        """Test LMS interpolation with specified number of points."""
        x_values = np.array([0, 1, 2, 3, 4, 5])
        l_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        m_values = np.array([100, 110, 120, 130, 140, 150])
        s_values = np.array([0.1, 0.12, 0.14, 0.16, 0.18, 0.2])

        # Test with different numbers of points
        l1, m1, s1 = interpolate_lms(x_values, l_values, m_values, s_values, 2.5, n_points=2)
        l2, m2, s2 = interpolate_lms(x_values, l_values, m_values, s_values, 2.5, n_points=4)

        # Both should be reasonable interpolations
        assert 0.2 < l1 < 0.4
        assert 0.2 < l2 < 0.4
        assert 110 < m1 < 140
        assert 110 < m2 < 140
        assert 0.12 < s1 < 0.18
        assert 0.12 < s2 < 0.18

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with very small values
        assert normal_cdf(0.0001) > 0.5
        assert normal_cdf(-0.0001) < 0.5

        # Test calculate_value_for_z_score with zero z-score
        value = calculate_value_for_z_score(0.0, 0.2, 100.0, 0.1)
        assert abs(value - 100.0) < 0.001

        # Test calculate_z_score with mu value
        z_score = calculate_z_score(100.0, 0.2, 100.0, 0.1)
        assert abs(z_score - 0.0) < 0.001

    def test_numpy_types(self):
        """Test that functions work with numpy types."""
        # Test with numpy scalars
        z_np = np.float64(1.0)
        result = normal_cdf(z_np)
        assert isinstance(result, float)
        assert abs(result - 0.8413) < 0.001

        # Test with numpy arrays in interpolation
        x_vals = np.linspace(0, 4, 5)
        y_vals = np.linspace(0, 40, 5)
        result = interpolate_array(x_vals, y_vals, 2.0)
        assert isinstance(result, float)
        assert abs(result - 20.0) < 0.001
