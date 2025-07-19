import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import norm


def normal_cdf(z: float) -> float:
    """
    Convert a z-score to its percentile (0-100).

    :param z: The z-score.
    :return: The percentile (0-100).
    """

    return norm.cdf(z).item()


def calculate_value_for_z_score(z_score: float, lamb: float, mu: float, sigm: float) -> float:
    """
    Calculate the value for a given z-score based on the LMS method.

    :param z_score: The z-score to calculate the value for.
    :param lamb: The L parameter from the LMS method.
    :param mu: The M parameter from the LMS method.
    :param sigm: The S parameter from the LMS method.
    :return: The calculated value.
    """
    z_score = float(z_score)
    lamb = float(lamb)
    mu = float(mu)
    sigm = float(sigm)

    if lamb == 0:
        return mu * (1 + sigm * z_score)

    return mu * pow(1 + lamb * sigm * z_score, 1 / lamb)


def calculate_z_score(value: float, lamb: float, mu: float, sigm: float) -> float:
    """
    Calculate the z-score for a given value based on the LMS method.

    :param value: The value to calculate the z-score for.
    :param l: The L parameter from the LMS method.
    :param m: The M parameter from the LMS method.
    :param s: The S parameter from the LMS method.
    :return: The calculated z-score.
    """
    value = float(value)
    lamb = float(lamb)
    mu = float(mu)
    sigm = float(sigm)

    if lamb == 0:
        return (value / mu - 1) / sigm

    return (pow(value / mu, lamb) - 1) / (lamb * sigm)


def estimate_lms_from_sd(z_score_idx: np.ndarray, z_score_values: np.ndarray) -> tuple[float, float, float]:
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

    (lambda_fit, sigma_fit), _ = curve_fit(lms_func, z_score_idx, z_score_values, p0=[0.1, S0])

    return lambda_fit, mu, sigma_fit


def interpolate_array(x: int | float, x_values: np.ndarray, y_values: np.ndarray, n_points: int = 4) -> float:
    """
    Interpolate LMS parameters for a given x using the closest points from provided data.

    :param x_values: Array of x-coordinates (must be numeric and sortable).
    :param y_values: Array of y-coordinates corresponding to x_values.
    :param x: The x-value at which to interpolate.
    :param n_points: float of closest points to use for interpolation (default 4).
    :return: Interpolated value as Decimal.
    """
    if n_points == -1:
        return np.interp(float(x), x_values, y_values).item()

    # Find n_points closest ages
    idx_sorted = np.argsort(np.abs(x_values - float(x)))
    idxs = np.sort(idx_sorted[:n_points])

    # Use numpy.interp for 1D interpolation
    return np.interp(float(x), x_values[idxs], y_values[idxs]).item()


def interpolate_lms(
    x: int | float,
    x_values: np.ndarray,
    l_values: np.ndarray,
    m_values: np.ndarray,
    s_values: np.ndarray,
    n_points: int = 4,
) -> tuple[float, float, float]:
    """
    Interpolate LMS parameters for a given x using the closest points from provided data.

    :param x_values: Array of x-coordinates (must be numeric and sortable).
    :param l_values: Array of L values corresponding to x_values.
    :param m_values: Array of M values corresponding to x_values.
    :param s_values: Array of S values corresponding to x_values.
    :param x: The x-value at which to interpolate.
    :param n_points: float of closest points to use for interpolation (default 4).
    :return: Interpolated tuple (L, M, S) as Decimals.
    """

    if x < x_values[0] or x > x_values[-1]:
        raise ValueError(f"x {x} is out of bounds ({x_values[0]} - {x_values[-1]})")

    idx_sorted = np.argsort(np.abs(x_values - float(x)))
    idxs = np.sort(idx_sorted[:n_points])

    l_interp = interpolate_array(x, x_values[idxs], l_values[idxs], -1)
    m_interp = interpolate_array(x, x_values[idxs], m_values[idxs], -1)
    s_interp = interpolate_array(x, x_values[idxs], s_values[idxs], -1)

    return l_interp, m_interp, s_interp
