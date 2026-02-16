"""Functional API for developmental milestone queries."""

import pandas as pd

from pygrowthstandards.data.development.load import load_milestone_reference
from pygrowthstandards.typing.development import DataSourceType, MilestoneDomainType

# Cache for loaded milestone data
_MILESTONE_CACHE: dict[DataSourceType | None, pd.DataFrame] = {}


def _get_milestone_data(source: DataSourceType | None = None) -> pd.DataFrame:
    """Get cached milestone reference data.

    Args:
        source: Optional source filter.

    Returns:
        DataFrame with milestone data.
    """
    if source not in _MILESTONE_CACHE:
        table = load_milestone_reference(source=source)
        _MILESTONE_CACHE[source] = table.milestones

    return _MILESTONE_CACHE[source]


def get_milestones_for_age(age_days: int, source: DataSourceType = "brazil", domain: MilestoneDomainType | None = None) -> pd.DataFrame:
    """Get milestones applicable for a given age.

    Args:
        age_days: Age in days.
        source: Data source ("cdc" or "brazil").
        domain: Optional domain filter.

    Returns:
        DataFrame of applicable milestones.

    Example:
        >>> milestones = get_milestones_for_age(180, source="brazil")
        >>> print(len(milestones))
        5
    """
    df = _get_milestone_data(source)

    # Filter by age window
    mask = (df["age_window_min_days"] <= age_days) & (df["age_window_max_days"] >= age_days)

    # Apply domain filter if specified
    if domain is not None:
        mask = mask & (df["standardized_domain"] == domain)

    result = df[mask].copy()

    # Sort by domain and age window center
    result = result.sort_values(
        by=["standardized_domain", "age_window_center_days"],
        ignore_index=True,
    )

    return result


def check_milestone_expected(universal_concept_id: str, age_days: int, source: DataSourceType = "brazil") -> bool:
    """Check if a milestone is expected (within age window) for given age.

    Args:
        universal_concept_id: Milestone identifier.
        age_days: Age in days.
        source: Data source ("cdc" or "brazil").

    Returns:
        True if milestone is within expected age window.

    Example:
        >>> expected = check_milestone_expected("MOTOR_GROSS-SITS_WITHOUT_SUPPORT", 210, "brazil")
        >>> print(expected)
        True
    """
    df = _get_milestone_data(source)

    matches = df[df["universal_concept_id"] == universal_concept_id]

    if matches.empty:
        return False

    # Check if any matching milestone is within age window
    for _, milestone in matches.iterrows():
        if milestone["age_window_min_days"] <= age_days <= milestone["age_window_max_days"]:
            return True

    return False


def get_milestone(universal_concept_id: str, source: DataSourceType = "brazil") -> pd.Series | None:
    """Get a specific milestone by ID.

    Args:
        universal_concept_id: Milestone identifier.
        source: Data source ("cdc" or "brazil").

    Returns:
        Series with milestone data, or None if not found.

    Example:
        >>> milestone = get_milestone("SOCIAL-LOOKS_AT_A_FACE", "brazil")
        >>> if milestone is not None:
        ...     print(milestone["description_en"])
        Looks at a face
    """
    df = _get_milestone_data(source)

    matches = df[df["universal_concept_id"] == universal_concept_id]

    if matches.empty:
        return None

    # Return first match (there may be multiple with different age windows)
    return matches.iloc[0]


def get_milestones_by_domain(domain: MilestoneDomainType, source: DataSourceType = "brazil") -> pd.DataFrame:
    """Get all milestones for a specific domain.

    Args:
        domain: Domain to filter by.
        source: Data source ("cdc" or "brazil").

    Returns:
        DataFrame of milestones in the domain.

    Example:
        >>> motor_milestones = get_milestones_by_domain("MOTOR_GROSS", "brazil")
        >>> print(len(motor_milestones))
        15
    """
    df = _get_milestone_data(source)

    result = df[df["standardized_domain"] == domain].copy()

    # Sort by age window center
    result = result.sort_values(by=["age_window_center_days"], ignore_index=True)

    return result


def get_domains(source: DataSourceType = "brazil") -> list[MilestoneDomainType]:
    """Get list of available domains.

    Args:
        source: Data source ("cdc" or "brazil").

    Returns:
        List of domain identifiers.

    Example:
        >>> domains = get_domains("brazil")
        >>> print(domains)
        ['MOTOR_GROSS', 'MOTOR_FINE', 'SOCIAL_EMOTIONAL', 'COMMUNICATION', 'COGNITIVE', 'SENSORY']
    """
    df = _get_milestone_data(source)
    return df["standardized_domain"].unique().tolist()


def clear_cache() -> None:
    """Clear the milestone data cache.

    Use this if you need to reload the milestone reference data.
    """
    _MILESTONE_CACHE.clear()
