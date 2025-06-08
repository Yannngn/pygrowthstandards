import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from utils.stats import estimate_lms_from_sd


class StatsManager:
    def __init__(
        self,
        name: str,
        unit: str,
        min_age: int = 0,
        max_age: int = 1_000_000,
        age_key: str = "age",
    ):
        self.name = name
        self.slug = name.lower().replace(" ", "_").replace("-", "_")
        self.unit = unit
        self.min_age = min_age
        self.max_age = max_age
        self.age_key = age_key
        self.df = pd.DataFrame()  # Main DataFrame to hold all data
        self.uncut_df = None

    def add_csv(self, csv_path: str, sex: str = "M"):
        df = pd.read_csv(csv_path)
        df["sex"] = sex

        df = self._process_df(df)

        self.df = pd.concat([self.df, df], ignore_index=True, sort=False)

        # After concatenation, group by 'age' and 'sex', and combine non-NaN values
        self.df = self.df.groupby([self.age_key, "sex"], as_index=False).agg(
            lambda x: x.dropna().iloc[0] if x.notna().any() else pd.NA
        )

    def add_excel(self, excel_path: str, sheet: int = 0, sex: str = "M"):
        df = pd.read_excel(excel_path, sheet_name=sheet)
        df["sex"] = sex

        df = self._process_df(df)

        self.df = pd.concat([self.df, df], ignore_index=True, sort=False)

        # After concatenation, group by 'age' and 'sex', and combine non-NaN values
        self.df = self.df.groupby([self.age_key, "sex"], as_index=False).agg(
            lambda x: x.dropna().iloc[0] if x.notna().any() else pd.NA
        )

    def cut_data(self, min_age: int = 0, max_age: int = 1_000_000):
        self.uncut_df = self.df.copy()
        self.df = self.df[
            (self.df[self.age_key] >= min_age) & (self.df[self.age_key] <= max_age)
        ]

    def estimate_lms(self):
        # Example: Add columns for L, M, S using a vectorized approach or apply
        # This is a placeholder; real LMS estimation would be more complex
        if "l" in self.df.columns and "m" in self.df.columns and "s" in self.df.columns:
            return

        # Ensure sd3neg to sd3 are present
        required_sd = ["sd3neg", "sd2neg", "sd1neg", "sd0", "sd1", "sd2", "sd3"]
        if not all(col in self.df.columns for col in required_sd):
            raise ValueError("Required SD columns (sd3neg to sd3) are missing.")

        # Identify SD columns: sd3neg to sd3 are required, sd5neg to sd5 are optional
        sd_cols = [
            f"sd{i}neg" for i in range(5, 0, -1) if f"sd{i}neg" in self.df.columns
        ]
        sd_cols += [f"sd{i}" for i in range(0, 6) if f"sd{i}" in self.df.columns]

        # Create a new DataFrame with only the SD columns and age/sex
        sd_df = self.df[sd_cols].copy()

        sd_df[sd_cols] = sd_df[sd_cols].astype(float)
        zscores = [-int(sd[2]) if sd.endswith("neg") else int(sd[2]) for sd in sd_cols]

        # Use pandas apply to estimate LMS parameters for each row
        # Prepare zscores as a constant argument
        def lms_row(row):
            values = row.values.astype(float)
            l, m, s = estimate_lms_from_sd(np.array(zscores), values)
            return pd.Series({"l": l, "m": m, "s": s})

        lms_df = sd_df.apply(lms_row, axis=1)
        # Merge lms_df back to self.df on index to ensure correct alignment
        self.df = self.df.merge(lms_df, left_index=True, right_index=True)

    def to_dict(self) -> dict:
        self.cut_data(self.min_age, self.max_age)
        self.estimate_lms()

        return {
            "name": self.name,
            "unit": self.unit,
            "min_age": self.min_age,
            "max_age": self.max_age,
            "data": self.df.to_dict(orient="records"),
        }

    def _process_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process a DataFrame to ensure it has the correct structure and types.
        This is useful for ensuring that the DataFrame can be used in calculations.
        """
        # Normalize column names
        df.columns = [
            f"p{str(col)}" if str(col).isdigit() else str(col).lower()
            for col in df.columns
        ]

        # Handle first column (assumed to be age)
        age_col = df.columns[0]
        if "day" in age_col:
            df[self.age_key] = df[age_col].apply(lambda x: int(x))
            df.drop(columns=[age_col], inplace=True)
        elif "month" in age_col:
            df[self.age_key] = df[age_col].apply(lambda x: int(round(float(x) * 30.44)))
            df.drop(columns=[age_col], inplace=True)

        elif "week" in age_col:
            df[self.age_key] = df[age_col].apply(lambda x: int(float(x) * 7))
            df.drop(columns=[age_col], inplace=True)

        elif df[age_col].dtype == object and df[age_col].str.contains(r"\+").any():

            def parse_age(val):
                if isinstance(val, str) and "+" in val:
                    parts = val.split("+")
                    return int(parts[0]) * 7 + int(parts[1])
                return int(val)

            df[self.age_key] = df[age_col].apply(parse_age)
            df.drop(columns=[age_col], inplace=True)

        return df

    def to_json(self) -> str:
        """
        Convert the StatsManager data to a JSON string.
        """
        import json

        return json.dumps(self.to_dict(), indent=4)

    def restore_df(self):
        """
        Restore the original DataFrame before any cuts were made.
        This is useful for accessing the full dataset after cutting.
        """
        if self.uncut_df is not None:
            self.df = self.uncut_df.copy()
        else:
            raise ValueError("No uncut DataFrame available. Please cut data first.")
