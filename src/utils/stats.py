import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from scipy.stats import norm

from src.utils.errors import NoReferenceDataException


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


def numpy_calculate_value_for_z_score(z_score: float, lamb: np.ndarray, mu: np.ndarray, sigm: np.ndarray) -> np.ndarray:
    """
    Calculate values for z-score using the LMS method.

    :param z_score: A float z-score.
    :param lamb: An array of L parameters from the LMS method.
    :param mu: An array of M parameters from the LMS method.
    :param sigm: An array of S parameters from the LMS method.
    :return: An array of calculated values.
    """
    z_score = float(z_score)
    lamb = np.asarray(lamb, dtype=np.float64)
    mu = np.asarray(mu, dtype=np.float64)
    sigm = np.asarray(sigm, dtype=np.float64)

    result = np.empty_like(mu)
    mask = lamb == 0

    # For lamb == 0, use the alternative formula
    result[mask] = mu[mask] * (1 + sigm[mask] * z_score)
    # For lamb != 0, use the main formula
    result[~mask] = mu[~mask] * np.power(1 + lamb[~mask] * sigm[~mask] * z_score, 1 / lamb[~mask])

    return result


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


def numpy_calculate_z_score(value: float, lamb: np.ndarray, mu: np.ndarray, sigm: np.ndarray) -> np.ndarray:
    """
    Calculate z-scores for a given value based on the LMS method.

    :param value: The value to calculate the z-score for.
    :param lamb: An array of L parameters from the LMS method.
    :param mu: An array of M parameters from the LMS method.
    :param sigm: An array of S parameters from the LMS method.
    :return: An array of calculated z-scores.
    """
    value = float(value)
    lamb = np.asarray(lamb, dtype=np.float64)
    mu = np.asarray(mu, dtype=np.float64)
    sigm = np.asarray(sigm, dtype=np.float64)

    result = np.empty_like(mu)
    mask = lamb == 0

    # For lamb == 0, use the alternative formula
    result[mask] = (value / mu[mask] - 1) / sigm[mask]

    # For lamb != 0, use the main formula
    result[~mask] = (np.power(value / mu[~mask], lamb[~mask]) - 1) / (lamb[~mask] * sigm[~mask])

    return result


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

    # Set bounds for lambda and sigma to help optimizer
    bounds = ([-1.1, 1e-8], [1.1, 1])
    try:
        (lambda_fit, sigma_fit), _ = curve_fit(lms_func, z_score_idx, z_score_values, p0=[0.1, S0], bounds=bounds, maxfev=10000)
    except Exception as e:
        raise RuntimeError(f"Curve fitting failed: {e}")

    return lambda_fit, mu, sigma_fit


def interpolate_array(x: int | float, x_values: np.ndarray, y_values: np.ndarray, n_points: int = 5) -> float:
    """
    Interpolate LMS parameters for a given x using the closest points from provided data.
    Uses cubic spline interpolation if enough points, otherwise falls back to linear.

    :param x_values: Array of x-coordinates (must be numeric and sortable).
    :param y_values: Array of y-coordinates corresponding to x_values.
    :param x: The x-value at which to interpolate.
    :param n_points: Number of closest points to use for interpolation (default 5).
    :return: Interpolated value as float.
    """
    if n_points == -1:
        n_points = 5  # Default to 5 points

    n_points = min(max(n_points, 2), len(x_values))  # At least 2, at most available points

    # Find n_points closest x_values
    idx_sorted = np.argsort(np.abs(x_values - float(x)))
    idxs = np.sort(idx_sorted[:n_points])

    x_sel = x_values[idxs]
    y_sel = y_values[idxs]

    kind = "cubic" if len(x_sel) >= 4 else "linear"
    # If all x_sel are equal (shouldn't happen), just return the value
    if np.allclose(x_sel, x_sel[0]):
        return float(y_sel[0])

    interpolator = interp1d(x_sel, y_sel, kind=kind, assume_sorted=True)
    return float(interpolator(x))


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
    :return: Interpolated tuple (L, M, S) as floats.
    """

    if x < x_values.min() or x > x_values.max():
        raise NoReferenceDataException("x", "x_values", int(x))

    distances = np.abs(x_values - float(x))
    idx_sorted = np.argsort(distances)

    idxs = np.array(idx_sorted[:n_points])
    sorted_indices = np.argsort(list(set(x_values[idxs])))  # because of add user data?

    l_interp = interpolate_array(x, x_values[idxs][sorted_indices], l_values[idxs][sorted_indices], -1)
    m_interp = interpolate_array(x, x_values[idxs][sorted_indices], m_values[idxs][sorted_indices], -1)
    s_interp = interpolate_array(x, x_values[idxs][sorted_indices], s_values[idxs][sorted_indices], -1)

    return l_interp, m_interp, s_interp
