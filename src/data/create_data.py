import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.data.objects import GrowthData

DATASETS = [
    "growth",
    "very_preterm_growth",
    "newborn_size",
]

SOURCES_FULL = [
    ("who-growth-reference-data", "who-child-growth-standards"),
    ("intergrowth-21st-postnatal-growth-preterm-infants",),
    ("intergrowth-21st-newborn-standards", "intergrowth-21st-newborn-size-very-preterm-infants"),
]

SOURCES = [
    "who",
    "intergrowth",
    "intergrowth",
]

NAMES = [
    ("growth", "child_growth"),
    ("very_preterm_growth",),
    ("birth", "very_preterm_birth"),
]

MEASUREMENT_TYPES = [
    (
        "body_mass_index",
        "head_circumference",
        "head_circumference_velocity",
        "length_velocity",
        "stature",
        "weight_height",
        "weight_length",
        "weight_velocity",
        "weight",
    ),
    ("head_circumference", "length", "weight"),
    ("head_circumference", "length", "weight"),
]

SEXES = ["m", "f"]

FORMATS = ["xlsx", "csv", "csv"]


def get_path(source_folder: str, source: str, name: str, measurement_type: str, sex: str, fmt: str) -> str:
    return f"data/raw/{source_folder}/{source}-{name}-{measurement_type}-{sex}.{fmt}"


def main():
    for sex in SEXES:
        for dataset, sources_full, source, names, measurement_types, fmt in zip(
            DATASETS, SOURCES_FULL, SOURCES, NAMES, MEASUREMENT_TYPES, FORMATS
        ):
            for measurement_type in measurement_types:
                try:
                    data = GrowthData(source, dataset, measurement_type, sex)
                    for name, source_full in zip(names, sources_full):
                        try:
                            path = get_path(source_full, source, name, measurement_type, sex, fmt)

                            if measurement_type != "weight_velocity":
                                data.add_xlsx(path) if fmt == "xlsx" else data.add_csv(path)
                                continue

                            data.add_xlsx(path.replace(".xlsx", "-1mon.xlsx")) if fmt == "xlsx" else data.add_csv(
                                path.replace(".csv", "-1mon.csv")
                            )
                            data.add_xlsx(path.replace(".xlsx", "-2mon.xlsx")) if fmt == "xlsx" else data.add_csv(
                                path.replace(".csv", "-2mon.csv")
                            )

                        except FileNotFoundError:
                            logging.warning(f"File not found: {path}. Skipping this dataset.")  # type: ignore[]
                            continue
                    if not data.datasets:
                        continue
                    data.to_csv("data/tabular")
                    data.to_json("data/functional")
                except ValueError as e:
                    logging.warning(f"Failed to process {source}-{dataset}-{measurement_type}-{sex}: {e}")


if __name__ == "__main__":
    main()
