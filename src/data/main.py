import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.data.objects import Dataset, GrowthData

DATASETS = ["newborn_size", "very_preterm_growth", "growth"]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Process growth data from CSV or XLSX files.")
    parser.add_argument(
        "inputs",
        type=str,
        nargs="+",
        help="Path(s) to the input CSV or XLSX file(s). You can specify multiple files separated by space.",
    )
    parser.add_argument("--source", type=str, help="Source of the growth data (e.g., 'intergrowth', 'who').")
    parser.add_argument("--name", type=str, help="Name of the growth data (e.g., 'newborn', 'very_preterm').")
    parser.add_argument("--output-dir", type=str, default="output", help="Directory to save the output files.")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format.")

    args = parser.parse_args()

    for input_file in args.inputs:
        if not os.path.exists(input_file):
            logging.error(f"Input file {input_file} does not exist.")
            return

    if not os.path.exists(args.output_dir):
        logging.info(f"Creating output directory: {args.output_dir}")
        os.makedirs(args.output_dir)

    datasets = []
    for input_file in args.inputs:
        if input_file.endswith(".csv"):
            dataset = Dataset.from_csv(input_file)
        elif input_file.endswith(".xlsx"):
            dataset = Dataset.from_xlsx(input_file)
        else:
            logging.error(f"Unsupported file format for {input_file}. Please provide a CSV or XLSX file.")
            return
        datasets.append(dataset)

    if not datasets:
        logging.error("No valid datasets loaded.")
        return

    # Ensure all datasets have the same source, name, and measurement_type
    first = datasets[0]
    for ds in datasets[1:]:
        if ds.source != first.source or ds.measurement_type != first.measurement_type:
            logging.error("All datasets must have the same source, name, and measurement_type.")
            return

    growth_data = GrowthData(source=first.source, name=first.name, measurement_type=first.measurement_type, sex=first.sex)
    for ds in datasets:
        growth_data.add_dataset(ds)

    if args.format == "csv":
        growth_data.to_csv(args.output_dir)
    elif args.format == "json":
        growth_data.to_json(args.output_dir)


if __name__ == "__main__":
    main()
