import glob
import os

import pandas as pd
from docling.document_converter import DocumentConverter

# some manual changes are needed to the csv files after this script runs


def intergrowth_convert_weeks_days(weeks_days: str) -> int:
    """
    This function converts a string representing weeks and days into total days.
    The input format is expected to be "X+Y", where X is the number of weeks and Y is the number of days.
    """
    if "+" not in weeks_days:
        return int(weeks_days) if weeks_days.isdigit() else 0
    parts = weeks_days.split("+")
    weeks = int(parts[0])
    days = int(parts[1])

    return weeks * 7 + days


def docling_extract_tables(converter: DocumentConverter, source: str) -> None:
    conv_res = converter.convert(source)

    tables = []
    for table in conv_res.document.tables:
        table_df: pd.DataFrame = table.export_to_dataframe()

        index = "days" if "+" in table_df.iat[1, 0] else "weeks"
        header = [index, "sd3neg", "sd2neg", "sd1neg", "sd0", "sd1", "sd2", "sd3"]
        if any(str(col).startswith("Centiles") for col in table_df.columns):
            header = [index, "5", "10", "25", "50", "75", "90", "95"]

        table_df.columns = header

        tables.append(table_df)

    element_csv_filename = os.path.join(source.replace(".pdf", ".csv"))

    if tables:
        combined_df = pd.concat(tables, ignore_index=True)

        if "days" in combined_df.columns:
            combined_df["days"] = combined_df["days"].apply(
                intergrowth_convert_weeks_days
            )

        combined_df.to_csv(element_csv_filename, index=False, header=header)


def main():
    source_list = glob.glob("data/raw/**/*.pdf")
    converter = DocumentConverter()

    for source in source_list:
        print(f"Processing {source}...")
        docling_extract_tables(converter, source)


if __name__ == "__main__":
    main()
