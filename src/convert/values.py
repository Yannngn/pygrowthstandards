def value_to_z_score(value: float, l: float, m: float, s: float) -> float:
    """Convert a value to a percentile using the LMS method.

    Args:
        value (float): The value to convert.
        l (float): The L parameter of the LMS method.
        m (float): The M parameter of the LMS method.
        s (float): The S parameter of the LMS method.

    Returns:
        float: The percentile corresponding to the value.
    """
    if s == 0:
        raise ValueError("Standard deviation (s) must not be zero.")
    return (value - m) / s


def value_to_percentile(value: float, l: float, m: float, s: float) -> float:
    """Convert a value to a percentile using the LMS method.

    Args:
        value (float): The value to convert.
        l (float): The L parameter of the LMS method.
        m (float): The M parameter of the LMS method.
        s (float): The S parameter of the LMS method.

    Returns:
        float: The percentile corresponding to the value.
    """
    if s == 0:
        raise ValueError("Standard deviation (s) must not be zero.")

    z_score = value_to_z_score(value, l, m, s)
    return 100 * (0.5 + 0.5 * (1 + z_score))  # Convert z-score to percentile


def percentile_to_zscore(percentile: float) -> float:
    """Convert a percentile to a z-score.

    Args:
        percentile (float): The percentile to convert.

    Returns:
        float: The z-score corresponding to the percentile.
    """
    if not (0 <= percentile <= 100):
        raise ValueError("Percentile must be between 0 and 100.")

    return (percentile / 100) * 2 - 1  # Convert percentile to z-score
