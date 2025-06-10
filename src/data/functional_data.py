import json
import os
from glob import glob
from typing import Literal

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "functional")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def transform_data(data_list: list[dict]) -> dict:
    keys = data_list[0].keys()
    result = {key: [] for key in keys}
    for item in data_list:
        for key in keys:
            result[key].append(item[key])
    return result


def process_json_file(filepath, sex: Literal["M", "F"]):
    with open(filepath, "r", encoding="utf-8") as f:
        content: dict = json.load(f)

    # Split data by sex
    data = [item for item in content["data"] if item.get("sex") == sex]

    _ = content.pop("data")

    content.update(transform_data(data))

    _ = content.pop("sex")

    return content


def main():
    json_files = glob(os.path.join(DATA_DIR, "*.json"))
    for json_file in json_files:
        for sex in ["M", "F"]:
            processed = process_json_file(json_file, sex)  # type: ignore
            out_path = os.path.join(
                OUTPUT_DIR,
                os.path.basename(json_file.replace(".json", f"_{sex.lower()}.json")),
            )
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(processed, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
