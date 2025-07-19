from abc import ABC

from src.utils.constants import SPECIAL_CASES, YEAR
from src.utils.errors import InvalidChoiceError


class Choices(ABC):
    @staticmethod
    def _test_item(key: str, value) -> bool:
        return not key.startswith("_") and not callable(value) and not isinstance(value, classmethod)

    @classmethod
    def choices(cls):
        """
        Returns a list of all choices defined in the class, excluding callables.
        """
        return [value for key, value in cls.__dict__.items() if cls._test_item(key, value)]

    @classmethod
    def names(cls):
        """
        Returns a list of all keys (names) defined in the class, excluding callables.
        """
        return [value[0] for key, value in cls.__dict__.items() if cls._test_item(key, value)]

    @classmethod
    def get_values(cls, name: str):
        """
        Returns the value of a specific choice by its name.
        Raises InvalidChoiceError if the choice does not exist.
        """
        for key, values in cls.choices():
            if name in key:
                return values

        raise InvalidChoiceError(name, cls.choices())


class AgeChoices(Choices):
    """(age_name, (age_group, start_days, end_days))"""

    ZERO_ONE_YEARS = ("0-1", ("growth", 0, int(1 * YEAR)))
    ZERO_TWO_YEARS = ("0-2", ("growth", 0, int(2 * YEAR)))
    TWO_FIVE_YEARS = ("2-5", ("growth", int(2 * YEAR), int(5 * YEAR)))
    FIVE_TEN_YEARS = ("5-10", ("growth", int(5 * YEAR), int(10 * YEAR)))
    TEN_NINETEEN_YEARS = ("10-19", ("growth", int(10 * YEAR), int(19 * YEAR)))
    # tables
    NEWBORN = ("newborn", ("newborn_size", 168, 300))  # Gestational age
    VERY_PRETERM = ("very_preterm", ("very_preterm_growth", 189, 448))  # Chronological age for very preterm infants

    @staticmethod
    def get_age_name(age_days: int, newborn: bool | None = False, very_preterm: bool | None = False, is_born: bool | None = True) -> str:
        if not is_born:
            raise ValueError("Age name cannot be determined for unborn children.")

        if newborn:
            return AgeChoices.NEWBORN[0]

        if very_preterm and age_days < AgeChoices.VERY_PRETERM[1][-1]:
            return AgeChoices.VERY_PRETERM[0]

        for k, v in sorted(AgeChoices.choices(), key=lambda x: x[1][-1]):
            if k in [AgeChoices.NEWBORN[0], AgeChoices.VERY_PRETERM[0], AgeChoices.ZERO_ONE_YEARS[0]]:
                continue

            if v[1] <= age_days < v[2]:
                return str(k)

        raise ValueError(f"Age {age_days} days does not fit into any defined age group.")

    @staticmethod
    def get_age_group(age_name: str) -> str:
        return AgeChoices.get_values(age_name)[0]


class MeasurementChoices(Choices):
    """(measurement_name, (alias, ...))"""

    STATURE = ("stature", ("stature", "lfa", "hfa", "lhfa", "length", "height", "length_height"))
    WEIGHT = ("weight", ("wfa", "weight"))
    HEAD_CIRCUMFERENCE = ("head_circumference", ("hcfa", "hc", "head_circumference"))
    BODY_MASS_INDEX = ("body_mass_index", ("bfa", "bmi", "body_mass_index"))
    WEIGHT_LENGTH_RATIO = ("weight_length", ("wlr", "weight_length", "weight_length_ratio"))
    WEIGHT_HEIGHT_RATIO = ("weight_height", ("whr", "weight_height", "weight_height_ratio"))
    WEIGHT_VELOCITY = ("weight_velocity", ("weight_velocity",))
    LENGTH_VELOCITY = ("length_velocity", ("length_velocity",))
    HEAD_CIRCUMFERENCE_VELOCITY = ("head_circumference_velocity", ("head_circumference_velocity",))

    @classmethod
    def get_measurement_name(cls, alias: str):
        """
        Returns the name of a specific choice by its value.
        Raises InvalidChoiceError if the value does not exist.
        """
        for key, values in cls.choices():
            if alias in values:
                return key

        raise InvalidChoiceError(alias, cls.choices())


class TableChoices(Choices):
    """(age_group_measurement_name, source-age_group-table_name)"""

    # Growth
    GROWTH_STATURE = ("growth_stature", "who-growth-stature")
    GROWTH_WEIGHT = ("growth_weight", "who-growth-weight")
    GROWTH_HEAD_CIRCUMFERENCE = ("growth_head_circumference", "who-growth-head_circumference")
    GROWTH_BODY_MASS_INDEX = ("growth_body_mass_index", "who-growth-body_mass_index")

    # Weight/Stature
    GROWTH_WEIGHT_LENGTH = ("growth_weight_length", "who-growth-weight_length")
    GROWTH_WEIGHT_HEIGHT = ("growth_weight_height", "who-growth-weight_height")

    # Velocity
    GROWTH_WEIGHT_VELOCITY = ("growth_weight_velocity", "who-growth-weight_velocity")
    GROWTH_LENGTH_VELOCITY = ("growth_length_velocity", "who-growth-length_velocity")
    GROWTH_CIRCUMFERENCE_VELOCITY = ("growth_head_circumference_velocity", "who-growth-head_circumference_velocity")

    # Preterm Growth
    VERY_PRETERM_LENGTH = ("very_preterm_growth_length", "intergrowth-very_preterm_growth-length")
    VERY_PRETERM_WEIGHT = ("very_preterm_growth_weight", "intergrowth-very_preterm_growth-weight")
    VERY_PRETERM_HEAD_CIRCUMFERENCE = ("very_preterm_growth_head_circumference", "intergrowth-very_preterm_growth-head_circumference")

    # Birth
    BIRTH_LENGTH = ("newborn_size_length", "intergrowth-newborn_size-length")
    BIRTH_WEIGHT = ("newborn_size_weight", "intergrowth-newborn_size-weight")
    BIRTH_HEAD_CIRCUMFERENCE = ("newborn_size_head_circumference", "intergrowth-newborn_size-head_circumference")

    @staticmethod
    def get_table_name(measurement_type: str, age_group: str) -> str:
        """Get table name using mapping dictionaries for cleaner logic."""

        age_group = AgeChoices.get_age_group(age_group)
        measurement_type = MeasurementChoices.get_measurement_name(measurement_type)

        if measurement_type not in SPECIAL_CASES:
            return f"{age_group}_{measurement_type}"

        for age_groups, override_type in SPECIAL_CASES[measurement_type].items():
            if age_group in age_groups:
                measurement_type = override_type

        return f"{age_group}_{measurement_type}"

    def get_table_source(self, measurement_type: str, age_group: str, sex: str = "M"):
        """
        Returns the source of the table based on measurement type, age group, and sex.
        """
        table_name = self.get_table_name(measurement_type, age_group)
        return f"{self.get_values(table_name)}_{sex.lower()}-lms.json"
