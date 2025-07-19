import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.data.objects import GrowthData

FILES_LIST = [
    (
        "who-growth-reference-data",
        "who",
        "growth",
        (
            "body_mass_index",
            "stature",
            "weight",
        ),
        ("m", "f"),
        "xlsx",
    ),
    (
        "who-child-growth-standards",
        "who",
        "child_growth",
        (
            "body_mass_index",
            "head_circumference_velocity",
            "head_circumference",
            "length_velocity",
            "stature",
            "weight_height",
            "weight_stature",
            "weight_velocity",
            "weight",
        ),
        ("m", "f"),
        "xlsx",
    ),
    (
        "intergrowth-21st-postnatal-growth-preterm-infants",
        "intergrowth",
        "very_preterm_growth",
        (
            "head_circumference",
            "stature",
            "weight_stature",
            "weight",
        ),
        ("m", "f"),
        "csv",
    ),
    (
        "intergrowth-21st-newborn-size-very-preterm-infants",
        "intergrowth",
        "very_preterm_newborn",
        (
            "head_circumference",
            "stature",
            "weight_stature",
            "weight",
        ),
        ("m", "f"),
        "csv",
    ),
    (
        "intergrowth-21st-newborn-standards",
        "intergrowth",
        "newborn",
        (
            "head_circumference",
            "stature",
            "weight",
        ),
        ("m", "f"),
        "csv",
    ),
]


def get_path(source_folder: str, source: str, name: str, measurement_type: str, sex: str, fmt: str) -> str:
    # lazy way to fix newborn to birth
    return f"data/raw/{source_folder}/{source}-{name.replace("newborn", "birth")}-{measurement_type}-{sex}.{fmt}"


def main():
    data = GrowthData()

    for values in FILES_LIST:
        source_folder, source, dataset, measurement_types, sexes, fmt = values
        for measurement_type in measurement_types:
            for sex in sexes:
                path = get_path(source_folder, source, dataset, measurement_type, sex, fmt)
                print(f"Processing file: {path}")
                try:
                    if measurement_type not in ["weight_velocity"]:
                        data.add_xlsx(path) if fmt == "xlsx" else data.add_csv(path)
                        continue

                    (data.add_xlsx(path.replace(".xlsx", "-1mon.xlsx")) if fmt == "xlsx" else data.add_csv(path.replace(".csv", "-1mon.csv")))
                    (data.add_xlsx(path.replace(".xlsx", "-2mon.xlsx")) if fmt == "xlsx" else data.add_csv(path.replace(".csv", "-2mon.csv")))

                except FileNotFoundError:
                    logging.warning(f"File not found: {path}. Skipping this dataset.")
                    continue

    data.to_csv("data")
    data.to_json("data")


if __name__ == "__main__":
    main()
