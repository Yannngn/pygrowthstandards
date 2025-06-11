import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import norm


def normal_cdf(z: float) -> float:
    """
    Convert a z-score to its percentile (0-100).

    :param z: The z-score.
    :return: The percentile (0-100).
    """
    return float(norm.cdf(z))


def calculate_z_score(
    value: float, l: float, m: float, s: float  # noqa: E741
) -> float:
    """
    Calculate the z-score for a given value based on the LMS method.

    :param value: The value to calculate the z-score for.
    :param l: The L parameter from the LMS method.
    :param m: The M parameter from the LMS method.
    :param s: The S parameter from the LMS method.
    :return: The calculated z-score.
    """
    if l == 0:
        return (value / m - 1) / s

    return ((value / m) ** l - 1) / (l * s)


def estimate_lms_from_sd(
    z_scores: np.ndarray, values: np.ndarray
) -> tuple[float | None, float | None, float | None]:
    """Estimate L, M, S parameters from SD values and z-scores."""

    mu = values[np.where(z_scores == 0)[0][0]].item() if 0 in z_scores else None

    if mu is None:
        return None, None, None

    def lms_func(z, _lambda, _sigma):
        # Avoid division by zero for L close to 0
        _lambda = np.clip(_lambda, -10, 10)
        _mu = float(mu)
        _sigma = np.clip(_sigma, 1e-8, None)
        with np.errstate(all="ignore"):
            return (
                _mu * np.power(1 + _lambda * _sigma * z, 1 / _lambda)
                if abs(_lambda) > 1e-6
                else _mu * np.exp(_sigma * z)
            )

    S0 = np.std(values) / float(mu) if float(mu) != 0 else 0.1
    try:
        popt, _ = curve_fit(lms_func, z_scores, values, p0=[0.1, S0], maxfev=10000)
        lambda_fit, sigma_fit = popt
        lamb = lambda_fit
        sigm = sigma_fit

    except Exception:
        return None, None, None

    return lamb, mu, sigm


# TODO: Remove TableData logic and make it a pure utility function
def interpolate_lms(
    zscores: list[dict], age_days: int, n_points: int = 4
) -> dict | None:
    """
    Interpolate LMS parameters for the given age_days using numpy and multiple points.

    :param zscores: List of LMS parameter dicts with 'age', 'l', 'm', 's'.
    :param age_days: Age in days to interpolate for.
    :param n_points: Number of nearest points to use for interpolation (default 4).
    :return: Interpolated dict with 'l', 'm', 's' or None if not possible.
    """

    if not zscores:
        return None

    age_key = "age" if "age" in zscores[0] else "gestational_age"

    ages = np.array([entry[age_key] for entry in zscores])
    l_vals = np.array([entry["l"] for entry in zscores])
    m_vals = np.array([entry["m"] for entry in zscores])
    s_vals = np.array([entry["s"] for entry in zscores])

    # Raise ValueError if out of bounds
    if age_days < ages[0] or age_days > ages[-1]:
        raise ValueError(
            f"age_days {age_days} is out of bounds ({ages[0]} - {ages[-1]})"
        )

    # Find n_points closest ages
    idx_sorted = np.argsort(np.abs(ages - age_days))
    idxs = np.sort(idx_sorted[:n_points])

    sel_ages = ages[idxs]
    sel_l = l_vals[idxs]
    sel_m = m_vals[idxs]
    sel_s = s_vals[idxs]

    # Use numpy.interp for 1D interpolation
    l_interp = np.interp(age_days, sel_ages, sel_l)
    m_interp = np.interp(age_days, sel_ages, sel_m)
    s_interp = np.interp(age_days, sel_ages, sel_s)

    return {"l": float(l_interp), "m": float(m_interp), "s": float(s_interp)}


def functional_interpolate_lms(
    age_list: list[int],
    l_list: list[float],
    m_list: list[float],
    s_list: list[float],
    age_days: int,
    n_points: int = 4,
) -> dict | None:
    """
    Interpolate LMS parameters for the given age_days using numpy and multiple points.

    :param zscores: List of LMS parameter dicts with 'age', 'l', 'm', 's'.
    :param age_days: Age in days to interpolate for.
    :param n_points: Number of nearest points to use for interpolation (default 4).
    :return: Interpolated dict with 'l', 'm', 's' or None if not possible.
    """

    # Raise ValueError if out of bounds
    if age_days < age_list[0] or age_days > age_list[-1]:
        raise ValueError(
            f"age_days {age_days} is out of bounds ({age_list[0]} - {age_list[-1]})"
        )

    ages = np.array(age_list)
    l_vals = np.array(l_list)
    m_vals = np.array(m_list)
    s_vals = np.array(s_list)

    # Find n_points closest ages
    idx_sorted = np.argsort(np.abs(ages - age_days))
    idxs = np.sort(idx_sorted[:n_points])

    sel_ages = ages[idxs]
    sel_l = l_vals[idxs]
    sel_m = m_vals[idxs]
    sel_s = s_vals[idxs]

    # Use numpy.interp for 1D interpolation
    l_interp = np.interp(age_days, sel_ages, sel_l)
    m_interp = np.interp(age_days, sel_ages, sel_m)
    s_interp = np.interp(age_days, sel_ages, sel_s)

    return {"l": float(l_interp), "m": float(m_interp), "s": float(s_interp)}
