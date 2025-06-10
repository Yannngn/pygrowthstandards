import os
from typing import Literal

from stats_dataframe import StatsManager


def file_pattern(
    source: Literal["who", "intergrowth"],
    name: Literal[
        "very-preterm-birth", "birth", "very-preterm-growth", "child-growth", "growth"
    ],
    metric: Literal[
        "wfa", "lhfa", "lfa", "hfa", "hcfa", "wfh", "wfl", "bfa", "bmi", "wlr"
    ],
    sex: Literal["M", "F"],
    stat: Literal["zscore", "centile"],
    ext: Literal["csv", "xlsx"] = "csv",
) -> str:
    return f'{source}_{name}_{metric}_{"boys" if sex == "M" else "girls"}_{"z" if stat == "zscore" else "perc"}.{ext}'


def one_dataset(
    name,
    source: Literal["who", "intergrowth"],
    dataset: Literal[
        "very-preterm-birth", "birth", "very-preterm-growth", "child-growth", "growth"
    ],
    metric: Literal[
        "wfa", "lhfa", "lfa", "hfa", "hcfa", "wfh", "wfl", "bfa", "bmi", "wlr"
    ],
    unit: Literal["cm", "m", "kg", "g", "kg/m2", "kg/m"],
    min_age: int,
    max_age: int,
    path: str,
    ext: Literal["csv", "xlsx"] = "csv",
):
    dm = StatsManager(name, unit, min_age, max_age)
    if ext == "csv":
        dm.add_csv(
            os.path.join(
                path, file_pattern(source, dataset, metric, "M", "zscore", ext)
            ),
            sex="M",
        )
        dm.add_csv(
            os.path.join(
                path, file_pattern(source, dataset, metric, "M", "centile", ext)
            ),
            sex="M",
        )
        dm.add_csv(
            os.path.join(
                path, file_pattern(source, dataset, metric, "F", "zscore", ext)
            ),
            sex="F",
        )
        dm.add_csv(
            os.path.join(
                path, file_pattern(source, dataset, metric, "F", "centile", ext)
            ),
            sex="F",
        )

    elif ext == "xlsx":
        dm.add_excel(
            os.path.join(
                path, file_pattern(source, dataset, metric, "M", "zscore", ext)
            ),
            sex="M",
        )
        dm.add_excel(
            os.path.join(
                path, file_pattern(source, dataset, metric, "M", "centile", ext)
            ),
            sex="M",
        )
        dm.add_excel(
            os.path.join(
                path, file_pattern(source, dataset, metric, "F", "centile", ext)
            ),
            sex="F",
        )
        dm.add_excel(
            os.path.join(
                path, file_pattern(source, dataset, metric, "F", "zscore", ext)
            ),
            sex="F",
        )

    with open(f"data/{dm.slug}.json", "w") as f:
        f.write(dm.to_json())


def handle_birth():
    source = "intergrowth"
    path = "data/raw/intergrowth-21st-newborn-size-very-preterm-infants"
    dataset = "very-preterm-birth"
    metric = "wfa"
    ext = "csv"

    # birth (joining with very preterm)
    dm = StatsManager(
        "Intergrowth 21st Birth Size Weight For Gestational Age",
        "kg",
        168,
        300,
        "gestational_age",
    )

    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "zscore", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "centile", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "zscore", ext)),
        sex="F",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "centile", ext)),
        sex="F",
    )

    path = "data/raw/intergrowth-21st-newborn-standards"
    dataset = "birth"

    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "zscore", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "centile", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "zscore", ext)),
        sex="F",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "centile", ext)),
        sex="F",
    )

    with open(f"data/{dm.slug}.json", "w") as f:
        f.write(dm.to_json())

    # birth (joining with very preterm)
    dm = StatsManager(
        "Intergrowth 21st Birth Size Length For Gestational Age",
        "cm",
        168,
        300,
        "gestational_age",
    )

    path = "data/raw/intergrowth-21st-newborn-size-very-preterm-infants"
    dataset = "very-preterm-birth"
    metric = "lfa"

    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "zscore", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "centile", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "zscore", ext)),
        sex="F",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "centile", ext)),
        sex="F",
    )

    path = "data/raw/intergrowth-21st-newborn-standards"
    dataset = "birth"

    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "zscore", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "centile", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "zscore", ext)),
        sex="F",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "centile", ext)),
        sex="F",
    )

    with open(f"data/{dm.slug}.json", "w") as f:
        f.write(dm.to_json())

    # birth (joining with very preterm)
    dm = StatsManager(
        "Intergrowth 21st Birth Size Head Circumference For Gestational Age",
        "cm",
        168,
        300,
        "gestational_age",
    )

    path = "data/raw/intergrowth-21st-newborn-size-very-preterm-infants"
    dataset = "very-preterm-birth"
    metric = "hcfa"

    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "zscore", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "centile", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "zscore", ext)),
        sex="F",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "centile", ext)),
        sex="F",
    )

    path = "data/raw/intergrowth-21st-newborn-standards"
    dataset = "birth"

    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "zscore", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "M", "centile", ext)),
        sex="M",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "zscore", ext)),
        sex="F",
    )
    dm.add_csv(
        os.path.join(path, file_pattern(source, dataset, metric, "F", "centile", ext)),
        sex="F",
    )

    with open(f"data/{dm.slug}.json", "w") as f:
        f.write(dm.to_json())


def handle_very_preterm():

    # very preterm
    one_dataset(
        "Intergrowth 21st Very Preterm Growth Weight For Age",
        "intergrowth",
        "very-preterm-growth",
        "wfa",
        "kg",
        0,
        int(64 * 7),  # 64 weeks
        "data/raw/intergrowth-21st-postnatal-growth-preterm-infants",
        "csv",
    )
    one_dataset(
        "Intergrowth 21st Very Preterm Growth Length For Age",
        "intergrowth",
        "very-preterm-growth",
        "lfa",
        "cm",
        0,
        int(64 * 7),  # 64 weeks
        "data/raw/intergrowth-21st-postnatal-growth-preterm-infants",
        "csv",
    )
    one_dataset(
        "Intergrowth 21st Very Preterm Growth Head Circumference For Age",
        "intergrowth",
        "very-preterm-growth",
        "hcfa",
        "cm",
        0,
        int(64 * 7),  # 64 weeks
        "data/raw/intergrowth-21st-postnatal-growth-preterm-infants",
        "csv",
    )


def handle_0_to_2():
    # 0-2
    one_dataset(
        "WHO Growth 0 to 2 Weight For Age",
        "who",
        "child-growth",
        "wfa",
        "kg",
        0,
        int(365.25 * 2),
        "data/raw/who-child-growth-standards",
        "xlsx",
    )
    one_dataset(
        "WHO Growth 0 to 2 Length For Age",
        "who",
        "child-growth",
        "lhfa",
        "cm",
        0,
        int(365.25 * 2),
        "data/raw/who-child-growth-standards",
        "xlsx",
    )
    one_dataset(
        "WHO Growth 0 to 2 Head Circumference For Age",
        "who",
        "child-growth",
        "hcfa",
        "cm",
        0,
        int(365.25 * 2),
        "data/raw/who-child-growth-standards",
        "xlsx",
    )
    one_dataset(
        "WHO Growth 0 to 2 Body Mass Index For Age",
        "who",
        "child-growth",
        "bfa",
        "kg/m2",
        0,
        int(365.25 * 2),
        "data/raw/who-child-growth-standards",
        "xlsx",
    )


def handle_2_to_5():
    # 2-5
    one_dataset(
        "WHO Growth 2 to 5 Weight For Age",
        "who",
        "child-growth",
        "wfa",
        "kg",
        int(365.25 * 2) + 1,
        int(365.25 * 5),
        "data/raw/who-child-growth-standards",
        "xlsx",
    )
    one_dataset(
        "WHO Growth 2 to 5 Height For Age",
        "who",
        "child-growth",
        "lhfa",
        "cm",
        int(365.25 * 2) + 1,
        int(365.25 * 5),
        "data/raw/who-child-growth-standards",
        "xlsx",
    )
    one_dataset(
        "WHO Growth 2 to 5 Head Circumference For Age",
        "who",
        "child-growth",
        "hcfa",
        "cm",
        int(365.25 * 2) + 1,
        int(365.25 * 5),
        "data/raw/who-child-growth-standards",
        "xlsx",
    )
    one_dataset(
        "WHO Growth 2 to 5 Body Mass Index For Age",
        "who",
        "child-growth",
        "bfa",
        "kg/m2",
        int(365.25 * 2) + 1,
        int(365.25 * 5),
        "data/raw/who-child-growth-standards",
        "xlsx",
    )


def handle_5_to_10():
    # 5-10
    one_dataset(
        "WHO Growth 5 to 10 Weight For Age",
        "who",
        "growth",
        "wfa",
        "kg",
        int(365.25 * 5 + 30.44),  # 5 years + 1 month
        int(365.25 * 10),
        "data/raw/who-growth-reference-data",
        "xlsx",
    )
    one_dataset(
        "WHO Growth 5 to 10 Height For Age",
        "who",
        "growth",
        "hfa",
        "cm",
        int(365.25 * 5 + 30.44),  # 5 years + 1 month
        int(365.25 * 10),
        "data/raw/who-growth-reference-data",
        "xlsx",
    )
    one_dataset(
        "WHO Growth 5 to 10 Body Mass Index For Age",
        "who",
        "growth",
        "bmi",
        "kg/m2",
        int(365.25 * 5 + 30.44),  # 5 years + 1 month
        int(365.25 * 10),
        "data/raw/who-growth-reference-data",
        "xlsx",
    )


def handle_10_to_19():
    # 10-19
    one_dataset(
        "WHO Growth 10 to 19 Height For Age",
        "who",
        "growth",
        "hfa",
        "cm",
        int(365.25 * 10 + 30.44),  # 10 years + 1 month
        int(365.25 * 19),
        "data/raw/who-growth-reference-data",
        "xlsx",
    )
    one_dataset(
        "WHO Growth 10 to 19 Body Mass Index For Age",
        "who",
        "growth",
        "bmi",
        "kg/m2",
        int(365.25 * 10 + 30.44),  # 10 years + 1 month
        int(365.25 * 19),
        "data/raw/who-growth-reference-data",
        "xlsx",
    )


def main():
    # handle_birth()
    handle_very_preterm()
    # handle_0_to_2()
    # handle_2_to_5()
    # handle_5_to_10()
    # handle_10_to_19()


if __name__ == "__main__":
    main()
