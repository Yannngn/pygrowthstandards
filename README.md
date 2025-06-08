# pygrowthstandards

A Python library for calculating and visualizing child growth standards using WHO and Intergrowth 21st reference data.

## Features

- Calculate z-scores and percentiles for height, weight, and BMI
- Support for WHO and Intergrowth 21st growth and birth standards
- Plot customizable growth charts for individual children

## Installation

```bash
git clone https://www.github.com/Yannngn/pygrowthstandards.git
```

## Quick Start

```python
import datetime

from pygrowthstandards import Calculator

calculator = Calculator.from_kid(birthday_date=datetime.date(2020, 1, 1), sex="M")
calculator.add_measurement(
    length_height=115.0,
    weight=21.0,
    head_circumference=52.0,
    date=datetime.date(2025, 6, 1),
)

calculator.add_measurements([[...], ...]) # list of measurements, follow the args order, use None if no data

print(calculator.display_results())

calculator.plot_measurements(m, output_path=f"weight_measurements_plot.png")
```

## Documentation

[TODO]

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
