from dataclasses import dataclass
from decimal import Decimal as D
from enum import StrEnum
from typing import Literal

from .constants import WEEK, YEAR

# Templates
X_TEMPLATE = D("0.00")
MU_TEMPLATE = D("0.0000")
LAMBDA_TEMPLATE = D("0.0000")
SIGMA_TEMPLATE = D("0.00000")


class DataSource(StrEnum):
    WHO = "who"
    INTERGROWTH = "intergrowth"


class DataSex(StrEnum):
    MALE = "M"
    FEMALE = "F"
    UNKNOWN = "U"


class DataXType(StrEnum):
    AGE = "age"
    GESTATIONAL_AGE = "gestational_age"
    STATURE = "stature"


class MeasurementType(StrEnum):
    STATURE = "stature"
    WEIGHT = "weight"
    WEIGHT_STATURE = "weight_stature"
    HEAD_CIRCUMFERENCE = "head_circumference"
    BODY_MASS_INDEX = "body_mass_index"
    WEIGHT_VELOCITY = "weight_velocity"
    STATURE_VELOCITY = "stature_velocity"
    HEAD_CIRCUMFERENCE_VELOCITY = "head_circumference_velocity"


class AgeGroup(StrEnum):
    NEWBORN = "newborn"
    VERY_PRETERM_NEWBORN = "very_preterm_newborn"
    VERY_PRETERM_GROWTH = "very_preterm_growth"
    # ZERO_ONE = "0-1"
    ZERO_TWO = "0-2"
    TWO_FIVE = "2-5"
    FIVE_TEN = "5-10"
    TEN_NINETEEN = "10-19"


class DevelopmentGoalSlug(StrEnum):
    LIFTS_HEAD_PRONE = "lifts-head-prone"
    REACTS_TO_SOUND = "reacts-to-sound"
    WATCHES_FACE = "watches-face"
    SOCIAL_SMILE = "social-smile"
    MAKES_SOUNDS = "makes-sounds"
    HOLDS_HEAD_STEADY = "holds-head-steady"
    BRINGS_HANDS_TOGETHER = "brings-hands-together"
    GRASPS_OBJECTS = "grasps-objects"
    MAKES_VOWEL_SOUNDS = "makes-vowel-sounds"
    TURNS_HEAD_TO_SOUND = "turns-head-to-sound"
    SITS_WITH_SUPPORT = "sits-with-support"
    ROLLS_OVER = "rolls-over"
    TRANSFERS_OBJECTS = "transfers-objects"
    BABBLES = "babbles"
    SITS_WITHOUT_SUPPORT = "sits-without-support"
    STARTS_CRAWLING = "starts-crawling"
    PINCER_GRASP = "pincer-grasp"
    PRODUCES_JARGON = "produces-jargon"
    STANDS_WITH_SUPPORT = "stands-with-support"
    FIRST_WORDS = "first-words"
    WALKS_WITH_SUPPORT = "walks-with-support"
    WALKS_ALONE = "walks-alone"
    POINTS_TO_WANTS = "points-to-wants"
    BUILDS_TOWER_TWO_BLOCKS = "builds-tower-two-blocks"
    SAYS_TEN_WORDS = "says-ten-words"
    KICKS_BALL = "kicks-ball"
    REMOVES_CLOTHING = "removes-clothing"
    RUNS = "runs"
    CLIMBS_STAIRS = "climbs-stairs"
    FORMS_SIMPLE_SENTENCES = "forms-simple-sentences"
    JUMPS_WITH_BOTH_FEET = "jumps-with-both-feet"
    IDENTIFIES_BODY_PARTS = "identifies-body-parts"
    DRESSES_SELF = "dresses-self"
    CONVERSES_IN_SENTENCES = "converses-in-sentences"
    STANDS_ON_ONE_FOOT = "stands-on-one-foot"
    RECOGNIZES_COLORS = "recognizes-colors"
    ASKS_TO_GO_TO_TOILET = "asks-to-go-to-toilet"
    HOPS_ON_ONE_FOOT = "hops-on-one-foot"
    TELLS_SIMPLE_STORIES = "tells-simple-stories"
    DRAWS_PERSON = "draws-person"
    DEFINES_WORDS = "defines-words"


# Type aliases using the enums
DataSourceType = Literal["who", "intergrowth"]
DataSexType = Literal["M", "F", "U"]
DataXTypeType = Literal["age", "gestational_age", "corrected_age", "stature"]
MeasurementTypeType = Literal[
    "stature",
    "weight",
    "weight_stature",
    "head_circumference",
    "body_mass_index",
    "weight_velocity",
    "stature_velocity",
    "head_circumference_velocity",
]
AgeGroupType = Literal[
    # "0-1",
    "0-2",
    "2-5",
    "5-10",
    "10-19",
    "newborn",
    "very_preterm_newborn",
    "very_preterm_growth",
]
TableNameType = Literal[
    "growth", "child_growth", "very_preterm_growth", "very_preterm_newborn", "newborn"
]

DevelopmentGoalType = Literal[
    "lifts-head-prone",
    "reacts-to-sound",
    "watches-face",
    "social-smile",
    "makes-sounds",
    "holds-head-steady",
    "brings-hands-together",
    "grasps-objects",
    "makes-vowel-sounds",
    "turns-head-to-sound",
    "sits-with-support",
    "rolls-over",
    "transfers-objects",
    "babbles",
    "sits-without-support",
    "starts-crawling",
    "pincer-grasp",
    "produces-jargon",
    "stands-with-support",
    "first-words",
    "walks-with-support",
    "walks-alone",
    "points-to-wants",
    "builds-tower-two-blocks",
    "says-ten-words",
    "kicks-ball",
    "removes-clothing",
    "runs",
    "climbs-stairs",
    "forms-simple-sentences",
    "jumps-with-both-feet",
    "identifies-body-parts",
    "dresses-self",
    "converses-in-sentences",
    "stands-on-one-foot",
    "recognizes-colors",
    "asks-to-go-to-toilet",
    "hops-on-one-foot",
    "tells-simple-stories",
    "draws-person",
    "defines-words",
]
DevelopmentStatusType = Literal["achieved", "slightly_delayed", "delayed"]


@dataclass(frozen=True)
class AgeGroupConfig:
    """Configuration for age groups with limits, x_type, and table name."""

    limits: tuple[int, int]
    x_type: DataXTypeType
    table_name: TableNameType

    def contains_age(self, age: int) -> bool:
        return self.limits[0] <= age <= self.limits[1]


@dataclass(frozen=True)
class MeasurementConfig:
    """Configuration for measurements with units and aliases."""

    unit: str
    aliases: frozenset[str] = frozenset()

    def matches_alias(self, alias: str) -> bool:
        return alias.lower() in self.aliases or alias == self.unit


@dataclass(frozen=True)
class DevelopmentGoalConfig:
    """
    Configuration for a development goal.

    Attributes:
    - slug: Unique identifier for the goal.
    - description: Description of the goal.
    - min_age_months: Minimum age (in months) for achieving the goal.
    - max_age_months: Maximum age (in months) for achieving the goal.
    """

    slug: str
    description: str
    min_age_months: int
    max_age_months: int


# Configuration mappings
AGE_GROUP_CONFIG: dict[AgeGroupType, AgeGroupConfig] = {
    AgeGroup.VERY_PRETERM_NEWBORN: AgeGroupConfig(
        (24 * WEEK, 33 * WEEK - 1), "gestational_age", "very_preterm_newborn"
    ),
    AgeGroup.NEWBORN: AgeGroupConfig(
        (33 * WEEK, 43 * WEEK - 1), "gestational_age", "newborn"
    ),
    AgeGroup.VERY_PRETERM_GROWTH: AgeGroupConfig(
        (27 * WEEK, 64 * WEEK), "corrected_age", "very_preterm_growth"
    ),  # TODO: chronological_age
    # AgeGroup.ZERO_ONE: AgeGroupConfig((0, int(round(1 * YEAR))), "age", "child_growth"),
    AgeGroup.ZERO_TWO: AgeGroupConfig((0, int(round(2 * YEAR))), "age", "child_growth"),
    AgeGroup.TWO_FIVE: AgeGroupConfig(
        (int(round(2 * YEAR)) + 1, int(round(5 * YEAR))), "age", "child_growth"
    ),
    AgeGroup.FIVE_TEN: AgeGroupConfig(
        (int(round(5 * YEAR)) + 1, int(round(10 * YEAR))), "age", "growth"
    ),
    AgeGroup.TEN_NINETEEN: AgeGroupConfig(
        (int(round(10 * YEAR)) + 1, int(round(19 * YEAR))), "age", "growth"
    ),
}  # type: ignore

MEASUREMENT_CONFIG: dict[MeasurementTypeType, MeasurementConfig] = {
    MeasurementType.STATURE: MeasurementConfig(
        "cm", frozenset({"lfa", "hfa", "lhfa", "sfa", "l", "h", "s"})
    ),
    MeasurementType.WEIGHT: MeasurementConfig("kg", frozenset({"wfa", "w"})),
    MeasurementType.HEAD_CIRCUMFERENCE: MeasurementConfig(
        "cm", frozenset({"hcfa", "hc"})
    ),
    MeasurementType.BODY_MASS_INDEX: MeasurementConfig(
        "kg/m²", frozenset({"bmi", "bfa"})
    ),
    MeasurementType.WEIGHT_STATURE: MeasurementConfig(
        "kg/cm",
        frozenset(
            {
                "wfs",
                "wfl",
                "wfh",
                "weight_length",
                "weight_height",
                "weight_for_stature",
                "weight_for_length",
                "weight_for_height",
            }
        ),
    ),
    MeasurementType.STATURE_VELOCITY: MeasurementConfig("cm/month"),
    MeasurementType.WEIGHT_VELOCITY: MeasurementConfig("kg/month"),
    MeasurementType.HEAD_CIRCUMFERENCE_VELOCITY: MeasurementConfig("cm/month"),
}  # type: ignore

DEVELOPMENT_GOALS = {
    "lifts-head-prone": DevelopmentGoalConfig(
        "lifts-head-prone", "Fica de bruços, levanta a cabeça", 0, 2
    ),
    "reacts-to-sound": DevelopmentGoalConfig(
        "reacts-to-sound", "Reage ao som (vira a cabeça na direção do barulho)", 0, 2
    ),
    "watches-face": DevelopmentGoalConfig(
        "watches-face", "Observa o rosto de quem fala com ele/ela", 1, 2
    ),
    "social-smile": DevelopmentGoalConfig(
        "social-smile",
        "Sorri quando alguém conversa com ele/ela (sorriso social)",
        1,
        3,
    ),
    "makes-sounds": DevelopmentGoalConfig("makes-sounds", "Emite sons/gritos", 1, 3),
    "holds-head-steady": DevelopmentGoalConfig(
        "holds-head-steady", "Sustenta a cabeça", 2, 4
    ),
    "brings-hands-together": DevelopmentGoalConfig(
        "brings-hands-together", "Junta as mãos na linha média do corpo", 2, 4
    ),
    "grasps-objects": DevelopmentGoalConfig(
        "grasps-objects", "Leva objetos à boca e agarra o que está em suas mãos", 3, 6
    ),
    "makes-vowel-sounds": DevelopmentGoalConfig(
        "makes-vowel-sounds", "Emite sons vocálicos (gugu, agu)", 3, 6
    ),
    "turns-head-to-sound": DevelopmentGoalConfig(
        "turns-head-to-sound",
        "Vira a cabeça na direção de um som que lhe chama a atenção",
        4,
        6,
    ),
    "sits-with-support": DevelopmentGoalConfig(
        "sits-with-support", "Senta com apoio", 4, 7
    ),
    "rolls-over": DevelopmentGoalConfig(
        "rolls-over", "Rola (vira de costas para a barriga e vice-versa)", 4, 7
    ),
    "transfers-objects": DevelopmentGoalConfig(
        "transfers-objects", "Transfere objetos de uma mão para outra", 5, 8
    ),
    "babbles": DevelopmentGoalConfig(
        "babbles", "Duplica sílabas (baba, gugu, dada)", 6, 9
    ),
    "sits-without-support": DevelopmentGoalConfig(
        "sits-without-support", "Senta sem apoio", 6, 9
    ),
    "starts-crawling": DevelopmentGoalConfig(
        "starts-crawling", "Começa a engatinhar ou arrastar-se", 7, 10
    ),
    "pincer-grasp": DevelopmentGoalConfig(
        "pincer-grasp",
        "Pega pequenos objetos com o movimento de pinça (polegar e indicador)",
        8,
        12,
    ),
    "produces-jargon": DevelopmentGoalConfig(
        "produces-jargon",
        "Produz jargões (fala com entonação, mas sem palavras claras)",
        9,
        12,
    ),
    "stands-with-support": DevelopmentGoalConfig(
        "stands-with-support", "Fica de pé com apoio", 9, 12
    ),
    "first-words": DevelopmentGoalConfig(
        "first-words",
        "Diz uma ou duas palavras com sentido (ex: 'água', 'mamã')",
        9,
        14,
    ),
    "walks-with-support": DevelopmentGoalConfig(
        "walks-with-support", "Anda com apoio ou segurando nos móveis", 10, 14
    ),
    "walks-alone": DevelopmentGoalConfig("walks-alone", "Anda sozinho", 11, 16),
    "points-to-wants": DevelopmentGoalConfig(
        "points-to-wants", "Aponta para o que quer", 12, 16
    ),
    "builds-tower-two-blocks": DevelopmentGoalConfig(
        "builds-tower-two-blocks", "Constrói torre com dois cubos", 12, 18
    ),
    "says-ten-words": DevelopmentGoalConfig(
        "says-ten-words", "Fala cerca de 10 palavras", 15, 21
    ),
    "kicks-ball": DevelopmentGoalConfig("kicks-ball", "Chuta uma bola", 15, 24),
    "removes-clothing": DevelopmentGoalConfig(
        "removes-clothing", "Tira algumas peças de roupa", 16, 24
    ),
    "runs": DevelopmentGoalConfig("runs", "Corre", 18, 24),
    "climbs-stairs": DevelopmentGoalConfig(
        "climbs-stairs", "Sobe escadas com ajuda", 18, 24
    ),
    "forms-simple-sentences": DevelopmentGoalConfig(
        "forms-simple-sentences",
        "Forma frases simples com duas palavras (ex: 'quer água')",
        18,
        26,
    ),
    "jumps-with-both-feet": DevelopmentGoalConfig(
        "jumps-with-both-feet", "Pula com ambos os pés", 24, 36
    ),
    "identifies-body-parts": DevelopmentGoalConfig(
        "identifies-body-parts", "Identifica e nomeia várias partes do corpo", 24, 36
    ),
    "dresses-self": DevelopmentGoalConfig(
        "dresses-self", "Veste-se sozinho (com alguma ajuda)", 30, 42
    ),
    "converses-in-sentences": DevelopmentGoalConfig(
        "converses-in-sentences", "Conversa usando frases completas", 36, 48
    ),
    "stands-on-one-foot": DevelopmentGoalConfig(
        "stands-on-one-foot", "Fica em um pé só por alguns segundos", 36, 48
    ),
    "recognizes-colors": DevelopmentGoalConfig(
        "recognizes-colors", "Reconhece e nomeia algumas cores", 36, 48
    ),
    "asks-to-go-to-toilet": DevelopmentGoalConfig(
        "asks-to-go-to-toilet",
        "Pede para ir ao banheiro (controle dos esfíncteres)",
        36,
        48,
    ),
    "hops-on-one-foot": DevelopmentGoalConfig(
        "hops-on-one-foot", "Salta em um pé só", 48, 60
    ),
    "tells-simple-stories": DevelopmentGoalConfig(
        "tells-simple-stories",
        "Conta histórias simples e relata acontecimentos",
        48,
        60,
    ),
    "draws-person": DevelopmentGoalConfig(
        "draws-person", "Desenha uma figura humana com cabeça, corpo e membros", 48, 60
    ),
    "defines-words": DevelopmentGoalConfig(
        "defines-words", "Define palavras simples (ex: 'O que é uma bola?')", 48, 60
    ),
}


class ChoiceValidator:
    """Utility class for validating and resolving choices."""

    @staticmethod
    def resolve_measurement_alias(alias: str) -> MeasurementTypeType | None:
        """Resolve measurement alias to canonical name."""
        alias_lower = alias.lower()
        for measurement, config in MEASUREMENT_CONFIG.items():
            # compare against the enum value (string) and configured aliases/units
            if measurement == alias_lower or config.matches_alias(alias_lower):
                return measurement
        return None

    @staticmethod
    def get_age_group_for_age(age: int, x_type: DataXTypeType) -> AgeGroupType | None:
        """Find the appropriate age group for given age and x_type."""
        for age_group, config in AGE_GROUP_CONFIG.items():
            if config.x_type == x_type and config.contains_age(age):
                return age_group
        return None

    @staticmethod
    def validate_choice(value: str, choices: frozenset[str]) -> bool:
        """Validate if value is in choices."""
        return value in choices

    @staticmethod
    def get_measurement_unit(measurement: MeasurementTypeType) -> str:
        """Get unit for measurement type."""
        return MEASUREMENT_CONFIG[measurement].unit

    @staticmethod
    def get_age_type_from_table(table_name: TableNameType) -> DataXTypeType | None:
        """Get age type for table name."""
        for _, config in AGE_GROUP_CONFIG.items():
            if config.table_name == table_name:
                return config.x_type
        return None

    @staticmethod
    def get_age_type_from_age_group(age_group: AgeGroupType) -> DataXTypeType | None:
        """Get age type for age group."""
        for key, config in AGE_GROUP_CONFIG.items():
            if key == age_group:
                return config.x_type
        return None

    @staticmethod
    def get_age_group_from_ages(
        age: int | None = None, gestational_age: int | None = None
    ) -> AgeGroupType | None:
        if gestational_age is None and age is None:
            raise ValueError("Either age or gestational_age must be provided.")

        if age is not None and gestational_age is None:
            return ChoiceValidator.get_age_group_for_age(age, "age")

        assert gestational_age is not None, (
            "Either age or gestational_age must be provided. Only for typing"
        )

        if AGE_GROUP_CONFIG["very_preterm_newborn"].contains_age(gestational_age):
            if not age:
                return "very_preterm_newborn"

            if AGE_GROUP_CONFIG["very_preterm_growth"].contains_age(
                age + gestational_age
            ):
                return "very_preterm_growth"

            return ChoiceValidator.get_age_group_for_age(age, "age")

        if not age:
            return "newborn"

        return ChoiceValidator.get_age_group_for_age(age, "age")

    @staticmethod
    def get_table_name_from_age_group(age_group: AgeGroupType) -> TableNameType | None:
        """Get table name for age group."""
        return AGE_GROUP_TABLE_NAME.get(age_group)  # type: ignore

    @staticmethod
    def validate_development_goal(
        slug: DevelopmentGoalSlug, child_age_months: int, achieved: bool
    ) -> str | None:
        """
        Validate if a child has achieved a development goal within the expected age range.

        Parameters:
        - slug: The slug of the development goal.
        - child_age_months: The child's age in months.
        - achieved: Whether the child has achieved the goal.

        Returns:
        - A message indicating the validation result, or None if no issues are found.
        """
        goal = DEVELOPMENT_GOALS.get(slug)
        if not goal:
            return f"Unknown development goal: {slug}"

        if achieved:
            return None  # No issues if the goal is achieved

        if child_age_months <= goal.max_age_months:
            return f"Child has not achieved '{goal.description}' but is within the expected age range."

        if child_age_months <= goal.max_age_months + 1:
            return f"Possible issue: Child is slightly delayed in achieving '{goal.description}'."

        return f"Developmental issue: Child has not achieved '{goal.description}' and is significantly delayed."


# Convenience functions
def resolve_measurement(alias: str) -> MeasurementTypeType:
    """Resolve measurement alias with error handling."""
    result = ChoiceValidator.resolve_measurement_alias(alias)
    if result is None:
        raise ValueError(f"Unknown measurement alias: {alias}")
    return result


def get_age_group(age: int, x_type: DataXTypeType = "age") -> AgeGroupType:
    """Get age group with error handling."""
    result = ChoiceValidator.get_age_group_for_age(age, x_type)
    if result is None:
        raise ValueError(f"No age group found for age {age} with x_type {x_type}")
    return result


# Backward compatibility - keep existing variables
DEVELOPMENT_GOAL_CHOICES = frozenset([e.value for e in DevelopmentGoalSlug])
DATA_SOURCE_CHOICES = frozenset([e.value for e in DataSource])
DATA_SEX_CHOICES = frozenset([e.value for e in DataSex])
DATA_X_CHOICES = frozenset([e.value for e in DataXType])
MEASUREMENT_TYPE_CHOICES = frozenset([e.value for e in MeasurementType])
AGE_GROUP_CHOICES = frozenset([e.value for e in AgeGroup])

# Legacy dictionaries (derived from configs)
UNITS = {measurement: config.unit for measurement, config in MEASUREMENT_CONFIG.items()}
AGE_GROUP_LIMITS = {
    age_group: config.limits for age_group, config in AGE_GROUP_CONFIG.items()
}
AGE_GROUP_X = {
    age_group: config.x_type for age_group, config in AGE_GROUP_CONFIG.items()
}
AGE_GROUP_TABLE_NAME = {
    age_group: config.table_name for age_group, config in AGE_GROUP_CONFIG.items()
}
MEASUREMENT_ALIASES = {
    measurement: config.aliases
    for measurement, config in MEASUREMENT_CONFIG.items()
    if config.aliases
}
