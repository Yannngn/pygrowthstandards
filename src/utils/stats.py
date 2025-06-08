import numpy as np
from scipy.optimize import curve_fit, minimize
from scipy.stats import norm


def normal_cdf(z: float) -> float:
    """
    Convert a z-score to its percentile (0-100).

    :param z: The z-score.
    :return: The percentile (0-100).
    """
    return float(norm.cdf(z))


def calculate_z_score(value: float, l: float, m: float, s: float) -> float:
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

    m = values[np.where(z_scores == 0)[0][0]].item() if 0 in z_scores else None

    if m is None:
        return None, None, None

    def lms_func(z, L, S):
        # Avoid division by zero for L close to 0
        L = np.clip(L, -10, 10)
        M = float(m)
        S = np.clip(S, 1e-8, None)
        with np.errstate(all="ignore"):
            return (
                M * np.power(1 + L * S * z, 1 / L)
                if abs(L) > 1e-6
                else M * np.exp(S * z)
            )

    S0 = np.std(values) / float(m) if float(m) != 0 else 0.1
    try:
        popt, _ = curve_fit(lms_func, z_scores, values, p0=[0.1, S0], maxfev=10000)
        L_fit, S_fit = popt
        l = L_fit
        s = S_fit

    except Exception:
        return None, None, None

    return l, m, s


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


def _estimate_lms_from_sd(zscores, values):
    """
    OLD
    Estimate LMS parameters from mean and values at given Z-scores.

    Args:
        zscores (array-like): Z-scores corresponding to the values. [-3, -2, -1, 0, 1, 2, 3]
        values (array-like): Observed values at the given Z-scores.

    Returns:
        tuple: (L, M, S)
            L: Box-Cox power
            M: Median
            S: Coefficient of variation
    """
    z_scores = np.asarray(zscores)
    values = np.asarray(values)
    # Find the value at z=0 for M (median)
    if 0 in z_scores:
        M = values[np.where(z_scores == 0)[0][0]]
    else:
        # Interpolate for z=0 if not present
        M = np.interp(0, z_scores, values)

    def residuals(params):
        L, S = params
        if S <= 0:
            return 1e6  # Penalize negative S
        # Avoid division by zero for L close to 0
        if np.isclose(L, 0):
            pred = M * np.exp(S * z_scores)
        else:
            pred = M * (1 + L * S * z_scores) ** (1 / L)
        return np.sum((values - pred) ** 2)

    # Initial guess: L=1 (normal), S from SD1 if possible
    if len(z_scores) >= 2 and z_scores[0] != z_scores[1]:
        S0 = (values[1] - values[0]) / ((z_scores[1] - z_scores[0]) * M)
    else:
        S0 = 0.1
    res = minimize(residuals, [1.0, S0], bounds=[(-2, 2), (1e-6, None)])
    L, S = res.x

    return L, M, S
