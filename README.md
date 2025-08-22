# pygrowthstandards

[![PyPI version](https://badge.fury.io/py/pygrowthstandards.svg)](https://badge.fury.io/py/pygrowthstandards)
[![Python Version](https://img.shields.io/pypi/pyversions/pygrowthstandards.svg)](https://pypi.org/project/pygrowthstandards)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://pypi.org/project/pygrowthstandards)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python package](https://github.com/Yannngn/pygrowthstandards/actions/workflows/python-package.yml/badge.svg)](https://github.com/Yannngn/pygrowthstandards/actions/workflows/python-package.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A Python library for calculating and visualizing child growth standards using data from the World Health Organization (WHO) and the INTERGROWTH-21st Project.

This toolkit provides a simple and flexible API to assess child growth by calculating z-scores and percentiles for common anthropometric measurements, including height, weight, BMI, and head circumference.

## Data Sources

This library implements standards from internationally recognized sources:

- **[WHO Child Growth Standards](https://www.who.int/tools/child-growth-standards):** For infants and children from birth to 5 years.
- **[WHO Growth Reference Data for 5-19 years](https://www.who.int/tools/growth-reference-data-for-5to19-years):** For school-aged children and adolescents.
- **[The INTERGROWTH-21st Project](https://intergrowth21.tghn.org/):** For newborn, preterm, and postnatal growth.

## Features

- Calculate z-scores and percentiles for stature (length/height), weight, BMI, and head circumference.
- Support for both WHO and INTERGROWTH-21st growth standards.
- A simple object-oriented `Calculator` for tracking a `Patient`'s measurements over time.
- A straightforward functional API for one-off calculations.
- Generate and save customizable growth charts.

## Installation

To install the latest stable release from PyPI:

```bash
pip install pygrowthstandards
```

### Development Installation

To install for development, clone the repository and install in editable mode using uv:

```bash
git clone https://github.com/Yannngn/pygrowthstandards.git
cd pygrowthstandards
uv venv --python 3.11
source .venv/bin/activate
uv sync
```

## Quick Start

### Object-Oriented Approach

The object-oriented API is ideal for tracking a patient's growth over time. It uses a `Patient` object to store measurements and a `Plotter` to visualize them.

```python
# filepath: main.py
import datetime
from pygrowthstandards.oop.patient import Patient
from pygrowthstandards.oop.measurement import MeasurementGroup
from pygrowthstandards.oop.plotter import Plotter

# 1. Create a Patient
patient = Patient(
    sex="M",
    birthday_date=datetime.date(2022, 1, 1),
)

# 2. Add measurements over time
measurements = [
    MeasurementGroup(date=datetime.date(2022, 7, 1), weight=8.6, stature=68.4, head_circumference=44.5),
    MeasurementGroup(date=datetime.date(2023, 1, 1), weight=10.2, stature=75.7, head_circumference=46.5),
    MeasurementGroup(date=datetime.date(2024, 1, 1), weight=12.6, stature=87.8, head_circumference=48.5),
]
for mg in measurements:
    patient.add_measurements(mg)

# 3. Calculate z-scores for all measurements
patient.calculate_all()

# 4. Display a summary table
print(patient.display_measurements())

# 5. Plot the growth charts
plotter = Plotter(patient)
plotter.plot(
    age_group="0-2",
    measurement_type="stature",
    show=False,
    output_path="stature_growth_chart.png"
)
```

#### Example Output

After running the above code, you can view the generated growth chart:

![Stature Growth Chart](results/user_table_0_2_stature.png)

### Functional Approach

For quick, single, stateless calculations, the functional API provides direct access to the z-score calculation engine. This is useful when you don't need to track a patient's history.

```python
# filepath: main.py
from pygrowthstandards import functional as F

# Calculate z-scores for various measurements and ages
z1 = F.zscore("stature", 50, "F", age_days=0, gestational_age=280)
z2 = F.zscore("weight", 5, "F", age_days=30)
z3 = F.zscore("head_circumference", 40, "F", age_days=180)
z4 = F.zscore("stature", 80, "F", age_days=365)
z5 = F.zscore("weight", 12, "F", age_days=730)
z6 = F.zscore("head_circumference", 48, "F", age_days=1460)

print(f"{z1:.2f}\n{z2:.2f}\n{z3:.2f}\n{z4:.2f}\n{z5:.2f}\n{z6:.2f}")
```

The output of this script is:

```
0.45
1.34
-1.64
2.33
0.36
-0.94
```

## Contributing

Contributions are welcome! Please feel free to open an issue to report a bug or suggest a feature, or submit a pull request with your improvements.

Before contributing, please set up the development environment and run the pre-commit hooks and tests.

```bash
# Install hooks
pre-commit install

# Run tests
pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

This package is built upon the publicly available data provided by the **World Health Organization (WHO)** and **The INTERGROWTH-21st Project**. We are grateful for their commitment to open data and global health.
