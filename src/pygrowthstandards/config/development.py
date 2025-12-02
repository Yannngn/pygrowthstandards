from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from pygrowthstandards.utils.date_utils import months_to_days


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


@dataclass(frozen=True)
class DevelopmentGoalConfig:
    """
    Configuration for a development goal.

    Attributes:
    - key: Unique identifier for the goal.
    - description: Description of the goal.
    - limits: Tuple of (min_age_days, max_age_days) for achieving the goal.
    """

    key: str
    description: str
    limits: tuple[int, int]

    def contains_age(self, age: int) -> bool:
        return self.limits[0] <= age <= self.limits[1]


# TODO: revise start and end limit in days;
DEVELOPMENT_GOALS = {
    # min/max months synced with data/raw/development_goals_pt.csv, converted to days
    "moro-reflex": DevelopmentGoalConfig("moro-reflex", "Reflexo de Moro (abre os braços ao susto/queda)", (0, months_to_days(1) - 1)),
    "flexed-posture": DevelopmentGoalConfig(
        "flexed-posture",
        "Postura fletida de recém-nascido (pernas e braços juntos)",
        (0, months_to_days(1) - 1),
    ),
    "watches-face": DevelopmentGoalConfig("watches-face", "Observa o rosto de quem fala com ele/ela", (months_to_days(1), months_to_days(3))),
    "comfort-discomfort-signs": DevelopmentGoalConfig(
        "comfort-discomfort-signs",
        "Demonstra conforto (relaxa/sorri) e desconforto (chora)",
        (months_to_days(1), months_to_days(3)),
    ),
    "fixates-gaze": DevelopmentGoalConfig("fixates-gaze", "Fixa o olhar em pessoas ou objetos", (months_to_days(1), months_to_days(4))),
    "lifts-head-prone": DevelopmentGoalConfig("lifts-head-prone", "De bruços, eleva a cabeça", (months_to_days(1), months_to_days(3))),
    "smiles-spontaneously": DevelopmentGoalConfig("smiles-spontaneously", "Sorri espontaneamente", (months_to_days(2), months_to_days(4))),
    "differentiates-day-night": DevelopmentGoalConfig(
        "differentiates-day-night", "Começa a diferenciar dia e noite", (months_to_days(2), months_to_days(4))
    ),
    "brings-to-midline": DevelopmentGoalConfig("brings-to-midline", "Leva mãos/posição à linha média", (months_to_days(2), months_to_days(5))),
    "holds-head-prone": DevelopmentGoalConfig(
        "holds-head-prone", "De bruços, sustenta a cabeça em apoio no antebraço", (months_to_days(2), months_to_days(5))
    ),
    "babbles": DevelopmentGoalConfig("babbles", "Emite sons / balbucia", (months_to_days(2), months_to_days(5))),
    "actively-assists": DevelopmentGoalConfig(
        "actively-assists", "Ajuda ativamente quando apoiado (não fica passivo)", (months_to_days(3), months_to_days(6))
    ),
    "rolls-supine-to-prone": DevelopmentGoalConfig(
        "rolls-supine-to-prone", "Rola da posição supina para prona", (months_to_days(4), months_to_days(7))
    ),
    "assists-pull-to-sit": DevelopmentGoalConfig(
        "assists-pull-to-sit", "Ajuda a levantar-se quando segurado pelas mãos", (months_to_days(4), months_to_days(7))
    ),
    "reacts-to-sound": DevelopmentGoalConfig(
        "reacts-to-sound", "Vira a cabeça em direção a sons/barulhos", (months_to_days(4), months_to_days(9))
    ),
    "responds-to-call": DevelopmentGoalConfig("responds-to-call", "Reconhece quando é chamado(a)", (months_to_days(6), months_to_days(9))),
    "sits-without-support": DevelopmentGoalConfig("sits-without-support", "Senta sem apoio", (months_to_days(6), months_to_days(10))),
    "transfers-objects": DevelopmentGoalConfig(
        "transfers-objects", "Transfere objetos de uma mão para outra", (months_to_days(6), months_to_days(10))
    ),
    "differentiates-familiar-strangers": DevelopmentGoalConfig(
        "differentiates-familiar-strangers",
        "Responde diferente a familiares e estranhos",
        (months_to_days(7), months_to_days(11)),
    ),
    "imitates-sounds-gestures": DevelopmentGoalConfig(
        "imitates-sounds-gestures", "Imita sons e gestos simples", (months_to_days(7), months_to_days(12))
    ),
    "crawls": DevelopmentGoalConfig("crawls", "Engatinha", (months_to_days(7), months_to_days(13))),
    "thumb-grasp": DevelopmentGoalConfig("thumb-grasp", "Pega objetos com o polegar", (months_to_days(10), months_to_days(15))),
    "says-one-word": DevelopmentGoalConfig(
        "says-one-word", "Fala uma palavra com sentido (ex.: mamãe)", (months_to_days(10), months_to_days(15))
    ),
    "uses-gestures": DevelopmentGoalConfig("uses-gestures", "Faz gestos (acena, dá tchau)", (months_to_days(10), months_to_days(15))),
    "walks-alone": DevelopmentGoalConfig("walks-alone", "Anda sozinho(a), raramente cai", (months_to_days(10), months_to_days(15))),
    "removes-clothing-item": DevelopmentGoalConfig("removes-clothing-item", "Tira uma peça de roupa", (months_to_days(13), months_to_days(21))),
    "two-to-three-word-phrases": DevelopmentGoalConfig(
        "two-to-three-word-phrases", "Combina 2-3 palavras", (months_to_days(13), months_to_days(24))
    ),
    "walks-away-independently": DevelopmentGoalConfig(
        "walks-away-independently", "Afasta-se andando com autonomia", (months_to_days(13), months_to_days(24))
    ),
    "feeds-self-hands": DevelopmentGoalConfig("feeds-self-hands", "Alimenta-se com as mãos", (months_to_days(13), months_to_days(24))),
    "runs-and-climbs-steps": DevelopmentGoalConfig("runs-and-climbs-steps", "Corre; sobe degraus", (months_to_days(14), months_to_days(24))),
    "plays-alongside-peers": DevelopmentGoalConfig(
        "plays-alongside-peers", "Aceita/acompanha outras crianças", (months_to_days(21), months_to_days(36))
    ),
    "says-own-name": DevelopmentGoalConfig("says-own-name", "Diz o próprio nome", (months_to_days(21), months_to_days(36))),
    "dresses-with-help": DevelopmentGoalConfig("dresses-with-help", "Veste-se com ajuda", (months_to_days(21), months_to_days(48))),
    "stands-on-one-foot": DevelopmentGoalConfig("stands-on-one-foot", "Fica em um pé só", (months_to_days(21), months_to_days(48))),
    "uses-sentences": DevelopmentGoalConfig("uses-sentences", "Usa frases", (months_to_days(21), months_to_days(48))),
    "begins-toilet-training": DevelopmentGoalConfig(
        "begins-toilet-training", "Inicia controle esfincteriano", (months_to_days(21), months_to_days(48))
    ),
    "names-two-colors": DevelopmentGoalConfig("names-two-colors", "Reconhece/nomina duas cores", (months_to_days(24), months_to_days(48))),
    "hops-on-one-foot": DevelopmentGoalConfig("hops-on-one-foot", "Pula com um pé", (months_to_days(24), months_to_days(60))),
    "plays-with-peers": DevelopmentGoalConfig("plays-with-peers", "Brinca com outras crianças", (months_to_days(24), months_to_days(48))),
    "imitates-daily-activities": DevelopmentGoalConfig(
        "imitates-daily-activities", "Imita atividades do dia a dia", (months_to_days(24), months_to_days(60))
    ),
    "dresses-alone": DevelopmentGoalConfig("dresses-alone", "Veste-se sozinho(a)", (months_to_days(36), months_to_days(60))),
    "jumps-alternating-feet": DevelopmentGoalConfig(
        "jumps-alternating-feet", "Pula alternando os pés", (months_to_days(36), months_to_days(72))
    ),
    "alternates-cooperation-aggression": DevelopmentGoalConfig(
        "alternates-cooperation-aggression",
        "Alterna cooperação e agressividade",
        (months_to_days(36), months_to_days(72)),
    ),
    "expresses-preferences": DevelopmentGoalConfig(
        "expresses-preferences", "Expressa preferências e ideias próprias", (months_to_days(36), months_to_days(72))
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


class DevelopmentStatus(StrEnum):
    ON_TRACK = "on_track"
    ACHIEVED = "achieved"
    SLIGHTLY_DELAYED = "slightly_delayed"
    DELAYED = "delayed"
    NOT_ACHIEVABLE = "not_achieved"
    NOT_VERIFIED = "not_verified"


DevelopmentStatusType = Literal["on_track", "achieved", "slightly_delayed", "delayed", "not_achieved", "not_verified"]

DEVELOPMENT_STATUS_CHOICES = frozenset([e.value for e in DevelopmentStatus])
