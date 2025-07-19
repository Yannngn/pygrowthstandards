from src.utils.choices import (
    AGE_GROUP_CHOICES,
    MEASUREMENT_TYPE_CHOICES,
    TABLE_NAME_CHOICES,
)


class InvalidChoiceError(ValueError):
    """
    Exception raised when an invalid choice is provided.
    """

    def __init__(self, choice, valid_choices):
        message = f"Invalid choice: {choice}. Valid choices are: {', '.join(map(str, valid_choices))}"
        super().__init__(message)


class InvalidTableNameError(ValueError):
    """
    Exception raised when an invalid Table Name choice is provided.
    """

    def __init__(self, choice):
        message = f"Invalid Table Name: {choice}. Valid choices are: {', '.join(map(str, TABLE_NAME_CHOICES))}"
        super().__init__(message)


class InvalidAgeGroupError(ValueError):
    """
    Exception raised when an invalid Age Group choice is provided.
    """

    def __init__(self, choice):
        message = f"Invalid Age Group: {choice}. Valid choices are: {', '.join(map(str, AGE_GROUP_CHOICES))}"
        super().__init__(message)


class InvalidMeasurementTypeError(ValueError):
    """
    Exception raised when an invalid Measurement Type choice is provided.
    """

    def __init__(self, choice):
        message = f"Invalid Measurement Type: {choice}. Valid choices are: {', '.join(map(str, MEASUREMENT_TYPE_CHOICES))}"
        super().__init__(message)


class InvalidKeyPairError(KeyError):
    """
    Exception raised when an invalid Age Group and Measurement Type pair is provided.
    """

    def __init__(self, age_group, measurement_type):
        message = f"Invalid Age Group and Measurement Type pair: ({age_group}, {measurement_type})."
        super().__init__(message)
