"""Developmental milestone configuration and lookup data."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


class DevelopmentGoals(StrEnum):
    """Canonical keys aligned to the developmental goals dataset."""
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
DevelopmentLanguageType = Literal["pt", "en"]


@dataclass(frozen=True)
class DevelopmentGoalConfig:
    """Configuration for a developmental goal and its age range.

    Attributes:
        key: Unique identifier for the goal.
        descriptions: Localized descriptions keyed by language code.
        min_age_months: Minimum age in months.
        max_age_months: Maximum age in months.
    """

    key: str
    descriptions: dict[DevelopmentLanguageType, str]
    min_age_months: int
    max_age_months: int


DEVELOPMENT_GOALS = {
    # min/max months synced with data/raw/development_goals_pt.csv
    "moro-reflex": DevelopmentGoalConfig(
        "moro-reflex",
        {
            "pt": "Reflexo de Moro (abre os braços ao susto/queda)",
            "en": "Moro reflex (opens arms in response to startle/fall)",
        },
        0,
        0,
    ),
    "flexed-posture": DevelopmentGoalConfig(
        "flexed-posture",
        {
            "pt": "Postura fletida de recém-nascido (pernas e braços juntos)",
            "en": "Newborn flexed posture (legs and arms tucked)",
        },
        0,
        0,
    ),
    "watches-face": DevelopmentGoalConfig(
        "watches-face",
        {
            "pt": "Observa o rosto de quem fala com ele/ela",
            "en": "Watches the face of the person speaking to them",
        },
        1,
        3,
    ),
    "comfort-discomfort-signs": DevelopmentGoalConfig(
        "comfort-discomfort-signs",
        {
            "pt": "Demonstra conforto (relaxa/sorri) e desconforto (chora)",
            "en": "Shows comfort (relaxes/smiles) and discomfort (cries)",
        },
        1,
        3,
    ),
    "fixates-gaze": DevelopmentGoalConfig(
        "fixates-gaze",
        {
            "pt": "Fixa o olhar em pessoas ou objetos",
            "en": "Fixates gaze on people or objects",
        },
        1,
        4,
    ),
    "lifts-head-prone": DevelopmentGoalConfig(
        "lifts-head-prone",
        {
            "pt": "De bruços, eleva a cabeça",
            "en": "In prone position, lifts head",
        },
        1,
        3,
    ),
    "smiles-spontaneously": DevelopmentGoalConfig(
        "smiles-spontaneously",
        {
            "pt": "Sorri espontaneamente",
            "en": "Smiles spontaneously",
        },
        2,
        4,
    ),
    "differentiates-day-night": DevelopmentGoalConfig(
        "differentiates-day-night",
        {
            "pt": "Começa a diferenciar dia e noite",
            "en": "Begins to differentiate day and night",
        },
        2,
        4,
    ),
    "brings-to-midline": DevelopmentGoalConfig(
        "brings-to-midline",
        {
            "pt": "Leva mãos/posição à linha média",
            "en": "Brings hands/posture to midline",
        },
        2,
        5,
    ),
    "holds-head-prone": DevelopmentGoalConfig(
        "holds-head-prone",
        {
            "pt": "De bruços, sustenta a cabeça em apoio no antebraço",
            "en": "In prone position, holds head with forearm support",
        },
        2,
        5,
    ),
    "babbles": DevelopmentGoalConfig(
        "babbles",
        {
            "pt": "Emite sons / balbucia",
            "en": "Makes sounds / babbles",
        },
        2,
        5,
    ),
    "actively-assists": DevelopmentGoalConfig(
        "actively-assists",
        {
            "pt": "Ajuda ativamente quando apoiado (não fica passivo)",
            "en": "Actively assists when supported (not passive)",
        },
        3,
        6,
    ),
    "rolls-supine-to-prone": DevelopmentGoalConfig(
        "rolls-supine-to-prone",
        {
            "pt": "Rola da posição supina para prona",
            "en": "Rolls from supine to prone",
        },
        4,
        7,
    ),
    "assists-pull-to-sit": DevelopmentGoalConfig(
        "assists-pull-to-sit",
        {
            "pt": "Ajuda a levantar-se quando segurado pelas mãos",
            "en": "Assists to sit when pulled by the hands",
        },
        4,
        7,
    ),
    "reacts-to-sound": DevelopmentGoalConfig(
        "reacts-to-sound",
        {
            "pt": "Vira a cabeça em direção a sons/barulhos",
            "en": "Turns head toward sounds/noises",
        },
        5,
        9,
    ),
    "responds-to-call": DevelopmentGoalConfig(
        "responds-to-call",
        {
            "pt": "Reconhece quando é chamado(a)",
            "en": "Recognizes when called",
        },
        6,
        9,
    ),
    "sits-without-support": DevelopmentGoalConfig(
        "sits-without-support",
        {
            "pt": "Senta sem apoio",
            "en": "Sits without support",
        },
        6,
        10,
    ),
    "transfers-objects": DevelopmentGoalConfig(
        "transfers-objects",
        {
            "pt": "Transfere objetos de uma mão para outra",
            "en": "Transfers objects from one hand to the other",
        },
        6,
        10,
    ),
    "differentiates-familiar-strangers": DevelopmentGoalConfig(
        "differentiates-familiar-strangers",
        {
            "pt": "Responde diferente a familiares e estranhos",
            "en": "Responds differently to familiar people and strangers",
        },
        7,
        11,
    ),
    "imitates-sounds-gestures": DevelopmentGoalConfig(
        "imitates-sounds-gestures",
        {
            "pt": "Imita sons e gestos simples",
            "en": "Imitates sounds and simple gestures",
        },
        7,
        12,
    ),
    "crawls": DevelopmentGoalConfig(
        "crawls",
        {
            "pt": "Engatinha",
            "en": "Crawls",
        },
        7,
        13,
    ),
    "thumb-grasp": DevelopmentGoalConfig(
        "thumb-grasp",
        {
            "pt": "Pega objetos com o polegar",
            "en": "Grasps objects with the thumb",
        },
        10,
        15,
    ),
    "says-one-word": DevelopmentGoalConfig(
        "says-one-word",
        {
            "pt": "Fala uma palavra com sentido (ex.: mamãe)",
            "en": "Says one meaningful word (e.g., mama)",
        },
        10,
        15,
    ),
    "uses-gestures": DevelopmentGoalConfig(
        "uses-gestures",
        {
            "pt": "Faz gestos (acena, dá tchau)",
            "en": "Uses gestures (waves, says bye-bye)",
        },
        10,
        15,
    ),
    "walks-alone": DevelopmentGoalConfig(
        "walks-alone",
        {
            "pt": "Anda sozinho(a), raramente cai",
            "en": "Walks alone, rarely falls",
        },
        10,
        15,
    ),
    "removes-clothing-item": DevelopmentGoalConfig(
        "removes-clothing-item",
        {
            "pt": "Tira uma peça de roupa",
            "en": "Removes one clothing item",
        },
        13,
        21,
    ),
    "two-to-three-word-phrases": DevelopmentGoalConfig(
        "two-to-three-word-phrases",
        {
            "pt": "Combina 2-3 palavras",
            "en": "Combines 2-3 words",
        },
        13,
        24,
    ),
    "walks-away-independently": DevelopmentGoalConfig(
        "walks-away-independently",
        {
            "pt": "Afasta-se andando com autonomia",
            "en": "Walks away independently",
        },
        13,
        24,
    ),
    "feeds-self-hands": DevelopmentGoalConfig(
        "feeds-self-hands",
        {
            "pt": "Alimenta-se com as mãos",
            "en": "Feeds self with hands",
        },
        13,
        24,
    ),
    "runs-and-climbs-steps": DevelopmentGoalConfig(
        "runs-and-climbs-steps",
        {
            "pt": "Corre; sobe degraus",
            "en": "Runs; climbs steps",
        },
        14,
        24,
    ),
    "plays-alongside-peers": DevelopmentGoalConfig(
        "plays-alongside-peers",
        {
            "pt": "Aceita/acompanha outras crianças",
            "en": "Plays alongside peers",
        },
        21,
        36,
    ),
    "says-own-name": DevelopmentGoalConfig(
        "says-own-name",
        {
            "pt": "Diz o próprio nome",
            "en": "Says own name",
        },
        21,
        36,
    ),
    "dresses-with-help": DevelopmentGoalConfig(
        "dresses-with-help",
        {
            "pt": "Veste-se com ajuda",
            "en": "Dresses with help",
        },
        21,
        48,
    ),
    "stands-on-one-foot": DevelopmentGoalConfig(
        "stands-on-one-foot",
        {
            "pt": "Fica em um pé só",
            "en": "Stands on one foot",
        },
        21,
        48,
    ),
    "uses-sentences": DevelopmentGoalConfig(
        "uses-sentences",
        {
            "pt": "Usa frases",
            "en": "Uses sentences",
        },
        21,
        48,
    ),
    "begins-toilet-training": DevelopmentGoalConfig(
        "begins-toilet-training",
        {
            "pt": "Inicia controle esfincteriano",
            "en": "Begins toilet training",
        },
        21,
        48,
    ),
    "names-two-colors": DevelopmentGoalConfig(
        "names-two-colors",
        {
            "pt": "Reconhece/nomina duas cores",
            "en": "Names two colors",
        },
        24,
        48,
    ),
    "hops-on-one-foot": DevelopmentGoalConfig(
        "hops-on-one-foot",
        {
            "pt": "Pula com um pé",
            "en": "Hops on one foot",
        },
        24,
        60,
    ),
    "plays-with-peers": DevelopmentGoalConfig(
        "plays-with-peers",
        {
            "pt": "Brinca com outras crianças",
            "en": "Plays with peers",
        },
        24,
        48,
    ),
    "imitates-daily-activities": DevelopmentGoalConfig(
        "imitates-daily-activities",
        {
            "pt": "Imita atividades do dia a dia",
            "en": "Imitates daily activities",
        },
        24,
        60,
    ),
    "dresses-alone": DevelopmentGoalConfig(
        "dresses-alone",
        {
            "pt": "Veste-se sozinho(a)",
            "en": "Dresses alone",
        },
        36,
        60,
    ),
    "jumps-alternating-feet": DevelopmentGoalConfig(
        "jumps-alternating-feet",
        {
            "pt": "Pula alternando os pés",
            "en": "Jumps alternating feet",
        },
        36,
        72,
    ),
    "alternates-cooperation-aggression": DevelopmentGoalConfig(
        "alternates-cooperation-aggression",
        {
            "pt": "Alterna cooperação e agressividade",
            "en": "Alternates cooperation and aggression",
        },
        36,
        72,
    ),
    "expresses-preferences": DevelopmentGoalConfig(
        "expresses-preferences",
        {
            "pt": "Expressa preferências e ideias próprias",
            "en": "Expresses preferences and own ideas",
        },
        36,
        72,
    ),
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


# Backward compatibility - keep existing variables
DEVELOPMENT_GOAL_CHOICES = frozenset([e.value for e in DevelopmentGoals])


def get_development_goal_description(goal: DevelopmentGoalType, lang: DevelopmentLanguageType = "pt") -> str:
    config = DEVELOPMENT_GOALS[goal]
    return config.descriptions.get(lang, config.descriptions["pt"])
