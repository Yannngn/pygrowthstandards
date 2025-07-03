# Data Files

1. Weight-for-age charts, Birth to 24 Months, LMS parameters and selected smoothed weight percentiles in kilograms, by age

2. Length-for-age charts, Birth to 24 Months, LMS parameters and selected smoothed recumbent length percentiles in centimeters, by age

3. Weight-for-length charts, LMS parameters and selected smoothed weight percentiles in kilograms, by recumbent length (in centimeters)

4. Head circumference-for-age charts, Birth to 24 Months, LMS parameters and selected smoothed head circumference percentiles in centimeters, by age

These files contain the L, M, and S parameters needed to generate exact percentiles and z-scores, along with the percentile values for the 3rd, 5th, 10th, 25th, 50th, 75th, 90th, 95th, and 97th percentiles by sex (`1=male; 2=female`) and single month of age. The smoothed 85th percentile values are included in the BMI-for-age and weight-for-stature tables. Age is listed at the half month point for the entire month; for example, 1.5 months represents 1.0–1.99 months or 1.0 month up to but not including 2.0 months of age. The only exception is birth, which represents the point at birth. To obtain L, M, and S values at finer age or length/stature intervals, interpolation could be used.

The LMS parameters are:

- **M**: the median,
- **S**: the generalized coefficient of variation,
- **L**: the power in the Box-Cox transformation.

To obtain the value (**X**) of a given physical measurement at a particular z-score or percentile, use the following equations:

For **L ≠ 0**:

```math
X = M \times (1 + L \times S \times Z)^{1/L}
```

For **L = 0**:

```math
X = M \times \exp(S \times Z)
```

where **L**, **M**, and **S** are the values from the appropriate table corresponding to the age in months of the child (**^** indicates exponentiation, and `\exp(X)` is the exponential function, _e_ to the power _X_). **Z** is the z-score that corresponds to the percentile. Z-scores correspond exactly to percentiles, e.g., z-scores of -1.881, -1.645, -1.282, -0.674, 0, 0.674, 1.036, 1.282, 1.645, and 1.881 correspond to the 3rd, 5th, 10th, 25th, 50th, 75th, 85th, 90th, 95th, and 97th percentiles, respectively.

**Example:**  
To obtain the 5th percentile of weight-for-age for a 9-month-old male, look up the L, M, and S values from the WTAGEINF table:

- L = -0.1600954
- M = 9.476500305
- S = 0.11218624

For the 5th percentile, use Z = -1.645. Using the equation above, the 5th percentile is calculated as **7.90 kg**.

To obtain the z-score (**Z**) and corresponding percentile for a given measurement (**X**), use the following equations:

For **L ≠ 0**:

```math
Z = \frac{(X/M)^L - 1}{L \times S}
```

For **L = 0**:

```math
Z = \frac{\ln(X/M)}{S}
```

where **X** is the physical measurement (e.g., weight, length, head circumference, stature, or calculated BMI value), and **L**, **M**, and **S** are the values from the appropriate table corresponding to the age in months of the child (or length/stature).

**Example:**  
To obtain the weight-for-age z-score of a 9-month-old male who weighs 9.7 kg, use the L, M, and S values from the WTAGEINF table:

- L = -0.1600954
- M = 9.476500305
- S = 0.11218624

Using the equation above, the z-score for this child is **0.207**, which corresponds to the 58th percentile.

Z-scores and corresponding percentiles can be obtained from standard normal distribution tables found in statistics textbooks or online. Many computer programs also have functions to convert z-scores to percentiles and vice versa.

# Instructions to download data:

> Linux or WSL

```bash
$ source data/raw/cdc/data.sh
```
