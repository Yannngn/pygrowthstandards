"""Custom error types for growth reference lookups."""


class NoReferenceDataException(Exception):
    """Raised when no reference data is found for the specified parameters."""

    def __init__(
        self,
        measurement_type: str,
        age_type: str,
        age_value: int | float,
        sex: str | None = None,
    ):
        """Initialize the exception with lookup context.

        Args:
            measurement_type: Measurement alias.
            age_type: Age axis type label.
            age_value: Age value used for lookup.
            sex: Optional sex identifier.
        """
        self.measurement_type = measurement_type
        self.age_type = age_type
        self.age_value = age_value
        self.sex = sex

        if sex:
            message = f"No reference data found for measurement type '{measurement_type}', age {age_value} {age_type}, sex '{sex}'"
        else:
            message = f"No reference data found for measurement type '{measurement_type}', age {age_value} {age_type}"

        super().__init__(message)


class InvalidChoicesError(KeyError):
    """Raised when a measurement is invalid for an age group."""

    def __init__(self, measurement_type: str | None, age_group: str | None) -> None:
        """Initialize the error message.

        Args:
            measurement_type: Measurement alias.
            age_group: Age group identifier.
        """
        message = f"Invalid measurement type '{measurement_type}' for age group '{age_group}'"
        super().__init__(message)
