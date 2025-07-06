from decimal import Decimal as D
from typing import TypeAlias

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import norm

Number: TypeAlias = D | float

# TODO: use utils.stats and adapt to Decimal


def normal_cdf(z: Number) -> D:
    """
    Convert a z-score to its percentile (0-100).

    :param z: The z-score.
    :return: The percentile (0-100).
    """
    z = float(z) if isinstance(z, D) else z

    return D(norm.cdf(z).round(6).item())


def calculate_z_score(value: Number, lamb: Number, mu: Number, sigm: Number) -> D:
    """
    Calculate the z-score for a given value based on the LMS method.

    :param value: The value to calculate the z-score for.
    :param l: The L parameter from the LMS method.
    :param m: The M parameter from the LMS method.
    :param s: The S parameter from the LMS method.
    :return: The calculated z-score.
    """

    value = D(value)
    lamb = D(lamb)
    mu = D(mu)
    sigm = D(sigm)

    if lamb == 0:
        return (value / mu - 1) / sigm

    return ((value / mu) ** lamb - 1) / (lamb * sigm)


def estimate_lms_from_sd(z_score_idx: np.ndarray, z_score_values: np.ndarray) -> tuple[D, D, D]:
    """Estimate L, M, S parameters from SD values and z-scores."""

    if 0 not in z_score_idx:
        raise ValueError("z_scores must contain a zero value for M estimation.")

    mu = z_score_values[np.where(z_score_idx == 0)[0][0]].round(4).item()

    if mu is None:
        raise ValueError("M (mu) could not be determined from z_scores and values.")

    def lms_func(z, _lambda, _sigma):
        # Avoid division by zero for L close to 0
        _lambda = np.clip(_lambda, -1.1, 1.1)
        _sigma = np.clip(_sigma, 1e-8, 1)

        if abs(_lambda) > 1e-8:
            return mu * np.power(1 + _lambda * _sigma * z, 1 / _lambda)

        return mu * np.exp(_sigma * z)

    S0 = np.std(z_score_values) / float(mu)

    popt, _ = curve_fit(lms_func, z_score_idx, z_score_values, p0=[0.1, S0])
    lambda_fit, sigma_fit = popt
    lamb = round(lambda_fit, 4)
    sigm = round(sigma_fit, 5)

    return D(lamb), D(mu), D(sigm)


def interpolate_array(x_values: np.ndarray, y_values: np.ndarray, x: int | Number, n_points: int = 4) -> D:
    """
    Interpolate LMS parameters for a given x using the closest points from provided data.

    :param x_values: Array of x-coordinates (must be numeric and sortable).
    :param y_values: Array of y-coordinates corresponding to x_values.
    :param x: The x-value at which to interpolate.
    :param n_points: Number of closest points to use for interpolation (default 4).
    :return: Interpolated value as Decimal.
    """
    if n_points == -1:
        return D(np.interp(float(x), x_values, y_values))

    # Find n_points closest ages
    idx_sorted = np.argsort(np.abs(x_values - float(x)))
    idxs = np.sort(idx_sorted[:n_points])

    # Use numpy.interp for 1D interpolation
    return D(np.interp(float(x), x_values[idxs], y_values[idxs]))


def interpolate_lms(
    x_values: np.ndarray, l_values: np.ndarray, m_values: np.ndarray, s_values: np.ndarray, x: int | Number, n_points: int = 4
) -> tuple[D, D, D]:
    """
    Interpolate LMS parameters for a given x using the closest points from provided data.

    :param x_values: Array of x-coordinates (must be numeric and sortable).
    :param l_values: Array of L values corresponding to x_values.
    :param m_values: Array of M values corresponding to x_values.
    :param s_values: Array of S values corresponding to x_values.
    :param x: The x-value at which to interpolate.
    :param n_points: Number of closest points to use for interpolation (default 4).
    :return: Interpolated tuple (L, M, S) as Decimals.
    """

    if x < x_values[0] or x > x_values[-1]:
        raise ValueError(f"x {x} is out of bounds ({x_values[0]} - {x_values[-1]})")

    idx_sorted = np.argsort(np.abs(x_values - float(x)))
    idxs = np.sort(idx_sorted[:n_points])

    m_interp = interpolate_array(x_values[idxs], m_values[idxs], x, -1)
    l_interp = interpolate_array(x_values[idxs], l_values[idxs], x, -1)
    s_interp = interpolate_array(x_values[idxs], s_values[idxs], x, -1)

    return l_interp, m_interp, s_interp
