import glob
import json

import numpy as np
from scipy.stats import norm


def lms_zscore(x, l, m, s):
    """Calculate z-score from LMS parameters."""
    if l == 0:
        return np.log(x / m) / s
    return ((x / m) ** l - 1) / (l * s)


def lms_centile(z):
    """Convert z-score to centile."""
    return norm.cdf(z) * 100


def main():
    json_files = glob.glob("data/*.json")  # Adjust path as needed

    for file in json_files:
        zscore_errors = []
        centile_errors = []
        with open(file) as f:
            print(f"Processing file: {file}")
            data = json.load(f)["data"]
            for entry in data:
                l, m, s = entry["l"], entry["m"], entry["s"]
                # SD scores
                for key in [
                    "sd5neg",
                    "sd4neg",
                    "sd3neg",
                    "sd2neg",
                    "sd1neg",
                    "sd0",
                    "sd1",
                    "sd2",
                    "sd3",
                    "sd4",
                    "sd5",
                ]:
                    sd_val = entry.get(key)
                    if sd_val is None:
                        continue
                    z_est = lms_zscore(sd_val, l, m, s)
                    true_z = {
                        "sd5neg": -5,
                        "sd4neg": -4,
                        "sd3neg": -3,
                        "sd2neg": -2,
                        "sd1neg": -1,
                        "sd0": 0,
                        "sd1": 1,
                        "sd2": 2,
                        "sd3": 3,
                        "sd4": 4,
                        "sd5": 5,
                    }[key]
                    zscore_errors.append(abs(z_est - true_z))
                # Centiles
                for key, true_p in [
                    ("p01", 0.1),
                    ("p1", 1),
                    ("p5", 5),
                    ("p10", 10),
                    ("p25", 25),
                    ("p50", 50),
                    ("p75", 75),
                    ("p90", 90),
                    ("p95", 95),
                    ("p99", 99),
                    ("p999", 99.9),
                ]:
                    p_val = entry.get(key)
                    if p_val is None:
                        continue
                    z_est = lms_zscore(p_val, l, m, s)
                    centile_est = lms_centile(z_est)
                    centile_errors.append(abs(centile_est - true_p))

        print(
            f"Z-score mean abs error: {np.mean(zscore_errors):.4f}, max abs error: {np.max(zscore_errors):.4f}"
        )
        print(
            f"Centile mean abs error: {np.mean(centile_errors):.4f}, max abs error: {np.max(centile_errors):.4f}"
        )


if __name__ == "__main__":
    main()
