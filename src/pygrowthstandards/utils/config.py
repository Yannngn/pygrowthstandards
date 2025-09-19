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
    VERY_PRETERM_GROWTH = "very_pre_term_growth"
    # ZERO_ONE = "0-1"
    ZERO_TWO = "0-2"
    TWO_FIVE = "2-5"
    FIVE_TEN = "5-10"
    TEN_NINETEEN = "10-19"


class DevelopmentGoals(StrEnum):
    # Canonical keys aligned to data/raw/development_goals_pt.csv
    MORO_REFLEX = "moro-reflex"
    FLEXED_POSTURE = "flexed-posture"
    WATCHES_FACE = "watches-face"
    COMFORT_DISCOMFORT_SIGNS = "comfort-discomfort-signs"
    FIXATES_GAZE = "fixates-gaze"
    LIFTS_HEAD_PRONE = "lifts-head-prone"
    SMILES_SPONTANEOUSLY = "smiles-spontaneously"
    DIFFERENTIATES_DAY_NIGHT = "differentiates-day-night"
    BRINGS_TO_MIDLINE = "brings-to-midline"
    HOLDS_HEAD_PRONE = "holds-head-prone"
    BABBLES = "babbles"
    ACTIVELY_ASSISTS = "actively-assists"
    ROLLS_SUPINE_TO_PRONE = "rolls-supine-to-prone"
    ASSISTS_PULL_TO_SIT = "assists-pull-to-sit"
    REACTS_TO_SOUND = "reacts-to-sound"
    RESPONDS_TO_CALL = "responds-to-call"
    SITS_WITHOUT_SUPPORT = "sits-without-support"
    TRANSFERS_OBJECTS = "transfers-objects"
    DIFFERENTIATES_FAMILIAR_STRANGERS = "differentiates-familiar-strangers"
    IMITATES_SOUNDS_GESTURES = "imitates-sounds-gestures"
    CRAWLS = "crawls"
    THUMB_GRASP = "thumb-grasp"
    SAYS_ONE_WORD = "says-one-word"
    USES_GESTURES = "uses-gestures"
    WALKS_ALONE = "walks-alone"
    REMOVES_CLOTHING_ITEM = "removes-clothing-item"
    TWO_TO_THREE_WORD_PHRASES = "two-to-three-word-phrases"
    WALKS_AWAY_INDEPENDENTLY = "walks-away-independently"
    FEEDS_SELF_HANDS = "feeds-self-hands"
    RUNS_AND_CLIMBS_STEPS = "runs-and-climbs-steps"
    PLAYS_ALONGSIDE_PEERS = "plays-alongside-peers"
    SAYS_OWN_NAME = "says-own-name"
    DRESSES_WITH_HELP = "dresses-with-help"
    STANDS_ON_ONE_FOOT = "stands-on-one-foot"
    USES_SENTENCES = "uses-sentences"
    BEGINS_TOILET_TRAINING = "begins-toilet-training"
    NAMES_TWO_COLORS = "names-two-colors"
    HOPS_ON_ONE_FOOT = "hops-on-one-foot"
    PLAYS_WITH_PEERS = "plays-with-peers"
    IMITATES_DAILY_ACTIVITIES = "imitates-daily-activities"
    DRESSES_ALONE = "dresses-alone"
    JUMPS_ALTERNATING_FEET = "jumps-alternating-feet"
    ALTERNATES_COOPERATION_AGGRESSION = "alternates-cooperation-aggression"
    EXPRESSES_PREFERENCES = "expresses-preferences"


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
TableNameType = Literal["growth", "child_growth", "very_preterm_growth", "very_preterm_newborn", "newborn"]

DevelopmentGoalType = Literal[
    "moro-reflex",
    "flexed-posture",
    "watches-face",
    "comfort-discomfort-signs",
    "fixates-gaze",
    "lifts-head-prone",
    "smiles-spontaneously",
    "differentiates-day-night",
    "brings-to-midline",
    "holds-head-prone",
    "babbles",
    "actively-assists",
    "rolls-supine-to-prone",
    "assists-pull-to-sit",
    "reacts-to-sound",
    "responds-to-call",
    "sits-without-support",
    "transfers-objects",
    "differentiates-familiar-strangers",
    "imitates-sounds-gestures",
    "crawls",
    "thumb-grasp",
    "says-one-word",
    "uses-gestures",
    "walks-alone",
    "removes-clothing-item",
    "two-to-three-word-phrases",
    "walks-away-independently",
    "feeds-self-hands",
    "runs-and-climbs-steps",
    "plays-alongside-peers",
    "says-own-name",
    "dresses-with-help",
    "stands-on-one-foot",
    "uses-sentences",
    "begins-toilet-training",
    "names-two-colors",
    "hops-on-one-foot",
    "plays-with-peers",
    "imitates-daily-activities",
    "dresses-alone",
    "jumps-alternating-feet",
    "alternates-cooperation-aggression",
    "expresses-preferences",
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
    - key: Unique identifier for the goal.
    - description: Description of the goal.
    - min_age_months: Minimum age (in months) for achieving the goal.
    - max_age_months: Maximum age (in months) for achieving the goal.
    """

    key: str
    description: str
    min_age_months: int
    max_age_months: int


# Configuration mappings
AGE_GROUP_CONFIG: dict[AgeGroupType, AgeGroupConfig] = {
    AgeGroup.VERY_PRETERM_NEWBORN: AgeGroupConfig((24 * WEEK, 33 * WEEK - 1), "gestational_age", "very_preterm_newborn"),
    AgeGroup.NEWBORN: AgeGroupConfig((33 * WEEK, 43 * WEEK - 1), "gestational_age", "newborn"),
    AgeGroup.VERY_PRETERM_GROWTH: AgeGroupConfig((27 * WEEK, 64 * WEEK), "corrected_age", "very_preterm_growth"),  # TODO: chronological_age
    # AgeGroup.ZERO_ONE: AgeGroupConfig((0, int(round(1 * YEAR))), "age", "child_growth"),
    AgeGroup.ZERO_TWO: AgeGroupConfig((0, int(round(2 * YEAR))), "age", "child_growth"),
    AgeGroup.TWO_FIVE: AgeGroupConfig((int(round(2 * YEAR)) + 1, int(round(5 * YEAR))), "age", "child_growth"),
    AgeGroup.FIVE_TEN: AgeGroupConfig((int(round(5 * YEAR)) + 1, int(round(10 * YEAR))), "age", "growth"),
    AgeGroup.TEN_NINETEEN: AgeGroupConfig((int(round(10 * YEAR)) + 1, int(round(19 * YEAR))), "age", "growth"),
}  # type: ignore

MEASUREMENT_CONFIG: dict[MeasurementTypeType, MeasurementConfig] = {
    MeasurementType.STATURE: MeasurementConfig("cm", frozenset({"lfa", "hfa", "lhfa", "sfa", "l", "h", "s"})),
    MeasurementType.WEIGHT: MeasurementConfig("kg", frozenset({"wfa", "w"})),
    MeasurementType.HEAD_CIRCUMFERENCE: MeasurementConfig("cm", frozenset({"hcfa", "hc"})),
    MeasurementType.BODY_MASS_INDEX: MeasurementConfig("kg/m²", frozenset({"bmi", "bfa"})),
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
    # min/max months synced with data/raw/development_goals_pt.csv
    "moro-reflex": DevelopmentGoalConfig("moro-reflex", "Reflexo de Moro (abre os braços ao susto/queda)", 0, 0),
    "flexed-posture": DevelopmentGoalConfig("flexed-posture", "Postura fletida de recém-nascido (pernas e braços juntos)", 0, 0),
    "watches-face": DevelopmentGoalConfig("watches-face", "Observa o rosto de quem fala com ele/ela", 1, 3),
    "comfort-discomfort-signs": DevelopmentGoalConfig(
        "comfort-discomfort-signs", "Demonstra conforto (relaxa/sorri) e desconforto (chora)", 1, 3
    ),
    "fixates-gaze": DevelopmentGoalConfig("fixates-gaze", "Fixa o olhar em pessoas ou objetos", 1, 4),
    "lifts-head-prone": DevelopmentGoalConfig("lifts-head-prone", "De bruços, eleva a cabeça", 1, 3),
    "smiles-spontaneously": DevelopmentGoalConfig("smiles-spontaneously", "Sorri espontaneamente", 2, 4),
    "differentiates-day-night": DevelopmentGoalConfig("differentiates-day-night", "Começa a diferenciar dia e noite", 2, 4),
    "brings-to-midline": DevelopmentGoalConfig("brings-to-midline", "Leva mãos/posição à linha média", 2, 5),
    "holds-head-prone": DevelopmentGoalConfig("holds-head-prone", "De bruços, sustenta a cabeça em apoio no antebraço", 2, 5),
    "babbles": DevelopmentGoalConfig("babbles", "Emite sons / balbucia", 2, 5),
    "actively-assists": DevelopmentGoalConfig("actively-assists", "Ajuda ativamente quando apoiado (não fica passivo)", 3, 6),
    "rolls-supine-to-prone": DevelopmentGoalConfig("rolls-supine-to-prone", "Rola da posição supina para prona", 4, 7),
    "assists-pull-to-sit": DevelopmentGoalConfig("assists-pull-to-sit", "Ajuda a levantar-se quando segurado pelas mãos", 4, 7),
    "reacts-to-sound": DevelopmentGoalConfig("reacts-to-sound", "Vira a cabeça em direção a sons/barulhos", 5, 9),
    "responds-to-call": DevelopmentGoalConfig("responds-to-call", "Reconhece quando é chamado(a)", 6, 9),
    "sits-without-support": DevelopmentGoalConfig("sits-without-support", "Senta sem apoio", 6, 10),
    "transfers-objects": DevelopmentGoalConfig("transfers-objects", "Transfere objetos de uma mão para outra", 6, 10),
    "differentiates-familiar-strangers": DevelopmentGoalConfig(
        "differentiates-familiar-strangers", "Responde diferente a familiares e estranhos", 7, 11
    ),
    "imitates-sounds-gestures": DevelopmentGoalConfig("imitates-sounds-gestures", "Imita sons e gestos simples", 7, 12),
    "crawls": DevelopmentGoalConfig("crawls", "Engatinha", 7, 13),
    "thumb-grasp": DevelopmentGoalConfig("thumb-grasp", "Pega objetos com o polegar", 10, 15),
    "says-one-word": DevelopmentGoalConfig("says-one-word", "Fala uma palavra com sentido (ex.: mamãe)", 10, 15),
    "uses-gestures": DevelopmentGoalConfig("uses-gestures", "Faz gestos (acena, dá tchau)", 10, 15),
    "walks-alone": DevelopmentGoalConfig("walks-alone", "Anda sozinho(a), raramente cai", 10, 15),
    "removes-clothing-item": DevelopmentGoalConfig("removes-clothing-item", "Tira uma peça de roupa", 13, 21),
    "two-to-three-word-phrases": DevelopmentGoalConfig("two-to-three-word-phrases", "Combina 2-3 palavras", 13, 24),
    "walks-away-independently": DevelopmentGoalConfig("walks-away-independently", "Afasta-se andando com autonomia", 13, 24),
    "feeds-self-hands": DevelopmentGoalConfig("feeds-self-hands", "Alimenta-se com as mãos", 13, 24),
    "runs-and-climbs-steps": DevelopmentGoalConfig("runs-and-climbs-steps", "Corre; sobe degraus", 14, 24),
    "plays-alongside-peers": DevelopmentGoalConfig("plays-alongside-peers", "Aceita/acompanha outras crianças", 21, 36),
    "says-own-name": DevelopmentGoalConfig("says-own-name", "Diz o próprio nome", 21, 36),
    "dresses-with-help": DevelopmentGoalConfig("dresses-with-help", "Veste-se com ajuda", 21, 48),
    "stands-on-one-foot": DevelopmentGoalConfig("stands-on-one-foot", "Fica em um pé só", 21, 48),
    "uses-sentences": DevelopmentGoalConfig("uses-sentences", "Usa frases", 21, 48),
    "begins-toilet-training": DevelopmentGoalConfig("begins-toilet-training", "Inicia controle esfincteriano", 21, 48),
    "names-two-colors": DevelopmentGoalConfig("names-two-colors", "Reconhece/nomina duas cores", 24, 48),
    "hops-on-one-foot": DevelopmentGoalConfig("hops-on-one-foot", "Pula com um pé", 24, 60),
    "plays-with-peers": DevelopmentGoalConfig("plays-with-peers", "Brinca com outras crianças", 24, 48),
    "imitates-daily-activities": DevelopmentGoalConfig("imitates-daily-activities", "Imita atividades do dia a dia", 24, 60),
    "dresses-alone": DevelopmentGoalConfig("dresses-alone", "Veste-se sozinho(a)", 36, 60),
    "jumps-alternating-feet": DevelopmentGoalConfig("jumps-alternating-feet", "Pula alternando os pés", 36, 72),
    "alternates-cooperation-aggression": DevelopmentGoalConfig(
        "alternates-cooperation-aggression", "Alterna cooperação e agressividade", 36, 72
    ),
    "expresses-preferences": DevelopmentGoalConfig("expresses-preferences", "Expressa preferências e ideias próprias", 36, 72),
}
# Canonical ordering of development goals (Brazil MoH / npmd_1.1.csv)
DEVELOPMENT_GOALS_ORDER: list[str] = [
    "moro-reflex",
    "flexed-posture",
    "watches-face",
    "comfort-discomfort-signs",
    "fixates-gaze",
    "lifts-head-prone",
    "smiles-spontaneously",
    "differentiates-day-night",
    "brings-to-midline",
    "holds-head-prone",
    "babbles",
    "actively-assists",
    "rolls-supine-to-prone",
    "assists-pull-to-sit",
    "reacts-to-sound",
    "responds-to-call",
    "sits-without-support",
    "transfers-objects",
    "differentiates-familiar-strangers",
    "imitates-sounds-gestures",
    "crawls",
    "thumb-grasp",
    "says-one-word",
    "uses-gestures",
    "walks-alone",
    "removes-clothing-item",
    "two-to-three-word-phrases",
    "walks-away-independently",
    "feeds-self-hands",
    "runs-and-climbs-steps",
    "plays-alongside-peers",
    "says-own-name",
    "dresses-with-help",
    "stands-on-one-foot",
    "uses-sentences",
    "begins-toilet-training",
    "names-two-colors",
    "hops-on-one-foot",
    "plays-with-peers",
    "imitates-daily-activities",
    "dresses-alone",
    "jumps-alternating-feet",
    "alternates-cooperation-aggression",
    "expresses-preferences",
]


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
    def get_age_group_from_ages(age: int | None = None, gestational_age: int | None = None) -> AgeGroupType | None:
        if gestational_age is None and age is None:
            raise ValueError("Either age or gestational_age must be provided.")

        if age is not None and gestational_age is None:
            return ChoiceValidator.get_age_group_for_age(age, "age")

        assert gestational_age is not None, "Either age or gestational_age must be provided. Only for typing"

        if AGE_GROUP_CONFIG["very_preterm_newborn"].contains_age(gestational_age):
            if not age:
                return "very_preterm_newborn"

            if AGE_GROUP_CONFIG["very_preterm_growth"].contains_age(age + gestational_age):
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
    def validate_development_goal(key: DevelopmentGoals, child_age_months: int, achieved: bool) -> str | None:
        """
        Validate if a child has achieved a development goal within the expected age range.

        Parameters:
        - key: The key of the development goal.
        - child_age_months: The child's age in months.
        - achieved: Whether the child has achieved the goal.

        Returns:
        - A message indicating the validation result, or None if no issues are found.
        """
        goal = DEVELOPMENT_GOALS.get(key)
        if not goal:
            return f"Unknown development goal: {key}"

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
DEVELOPMENT_GOAL_CHOICES = frozenset([e.value for e in DevelopmentGoals])
DATA_SOURCE_CHOICES = frozenset([e.value for e in DataSource])
DATA_SEX_CHOICES = frozenset([e.value for e in DataSex])
DATA_X_CHOICES = frozenset([e.value for e in DataXType])
MEASUREMENT_TYPE_CHOICES = frozenset([e.value for e in MeasurementType])
AGE_GROUP_CHOICES = frozenset([e.value for e in AgeGroup])

# Legacy dictionaries (derived from configs)
UNITS = {measurement: config.unit for measurement, config in MEASUREMENT_CONFIG.items()}
AGE_GROUP_LIMITS = {age_group: config.limits for age_group, config in AGE_GROUP_CONFIG.items()}
AGE_GROUP_X = {age_group: config.x_type for age_group, config in AGE_GROUP_CONFIG.items()}
AGE_GROUP_TABLE_NAME = {age_group: config.table_name for age_group, config in AGE_GROUP_CONFIG.items()}
MEASUREMENT_ALIASES = {measurement: config.aliases for measurement, config in MEASUREMENT_CONFIG.items() if config.aliases}
