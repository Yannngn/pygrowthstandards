import datetime

import pandas as pd


def str_dataframe(
    results: list[dict], date_list: list[datetime.date], age_list: list[int]
) -> str:
    # This helper function is added to format the output

    # Flatten results for DataFrame with MultiIndex columns
    rows = []
    columns = set()
    subkey_order = ["value", "z"]
    for idx, (result, date, age) in enumerate(
        zip(results, date_list, age_list, strict=False), 1
    ):
        row: dict = {("Idx", ""): idx}
        # Add measurement date and child age (in days)
        row[("Date", "")] = date
        row[("Age (days)", "")] = age
        columns.add(("Date", ""))
        columns.add(("Age (days)", ""))
        for mtype, mvals in result.items():
            for subkey in subkey_order:
                if subkey not in mvals:
                    continue
                row[(mtype, subkey)] = mvals[subkey]
                columns.add((mtype, subkey))
        rows.append(row)

    if not rows:
        return "No data to display."

    # Ensure consistent column order: Idx, Date, Age (days), then each measurement type with subkeys in order
    measurement_types = sorted(
        {mtype for mtype, _ in columns if mtype not in ["Idx", "Date", "Age (days)"]}
    )
    ordered_columns = [("Idx", ""), ("Date", ""), ("Age (days)", "")]
    for mtype in measurement_types:
        for subkey in subkey_order:
            if (mtype, subkey) not in columns:
                continue
            ordered_columns.append((mtype, subkey))

    df = pd.DataFrame(rows)
    df = df.reindex(columns=ordered_columns)
    df.columns = pd.MultiIndex.from_tuples(df.columns)  # type: ignore

    # Format float columns to 2 decimal places
    float_cols = df.select_dtypes(include="float").columns
    df[float_cols] = df[float_cols].map(
        lambda x: f"{x:.2f}" if pd.notnull(x) else pd.NA
    )

    pd.set_option("display.max_columns", None)
    # Use to_string with custom formatting for better visual separation
    return df.to_string(index=False, justify="center", col_space=6)
