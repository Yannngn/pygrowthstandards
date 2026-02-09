"""
Usage Examples: Comparison of Different API Styles

This file demonstrates how the same task can be accomplished using different
API styles, highlighting the benefits of each approach.

The task: Create a male patient born on 2022-01-01, add measurements over time,
calculate z-scores, display results, and generate a growth chart.
"""

print("=" * 80)
print("API STYLE COMPARISON")
print("Task: Create patient, add measurements, calculate, display, and plot")
print("=" * 80)


# =============================================================================
# Style 1: Current API (v0.1.3) - Imperative Style
# =============================================================================

print("\n" + "=" * 80)
print("STYLE 1: Current API (Imperative)")
print("=" * 80)

print("""
# Import statements
from pygrowthstandards import Patient, MeasurementGroup, Plotter
import datetime

# Create patient
patient = Patient(
    sex="M",
    birthday_date=datetime.date(2022, 1, 1)
)

# Add measurements one by one
patient.add_measurements(
    MeasurementGroup(date=datetime.date(2022, 7, 1), weight=8.6, stature=68.4)
)
patient.add_measurements(
    MeasurementGroup(date=datetime.date(2023, 1, 1), weight=10.2, stature=75.7)
)
patient.add_measurements(
    MeasurementGroup(date=datetime.date(2024, 1, 1), weight=12.6, stature=87.8)
)

# Calculate z-scores
patient.calculate_all()

# Display results
print(patient.display_measurements())

# Create plotter and generate chart
plotter = Plotter(patient)
plotter.plot(
    age_group="0-2",
    measurement_type="weight",
    show=False,
    output_path="weight_chart.png"
)
""")

print("Lines of code: ~22")
print("Imports required: 3")
print("Intermediate objects: 2 (patient, plotter)")
print("Pros: Explicit, familiar pattern")
print("Cons: Verbose, repetitive, many intermediate steps")


# =============================================================================
# Style 2: Enhanced OOP with Method Chaining
# =============================================================================

print("\n" + "=" * 80)
print("STYLE 2: Method Chaining (Fluent Interface)")
print("=" * 80)

print("""
# Import statements
from pygrowthstandards.oop import FluentPatient
import datetime

# Create, populate, calculate, and plot in one chain
patient = (FluentPatient(sex="M", birthday_date=datetime.date(2022, 1, 1))
    .measured_at(datetime.date(2022, 7, 1), weight=8.6, stature=68.4)
    .measured_at(datetime.date(2023, 1, 1), weight=10.2, stature=75.7)
    .measured_at(datetime.date(2024, 1, 1), weight=12.6, stature=87.8)
    .calculate_all()
    .plot("weight", age_group="0-2", show=False, output_path="weight_chart.png"))

# Display results
print(patient.display_measurements())
""")

print("Lines of code: ~9")
print("Imports required: 2")
print("Intermediate objects: 0")
print("Code reduction: 59% fewer lines")
print("Pros: Concise, readable, natural flow")
print("Cons: Long chains harder to debug")


# =============================================================================
# Style 3: Builder Pattern
# =============================================================================

print("\n" + "=" * 80)
print("STYLE 3: Builder Pattern (Declarative)")
print("=" * 80)

print("""
# Import statements
from pygrowthstandards.builders import PatientBuilder
from pygrowthstandards import Plotter

# Build patient declaratively
patient = (PatientBuilder()
    .male()
    .born_on("2022-01-01")
    .measured_at("2022-07-01", weight=8.6, stature=68.4)
    .measured_at("2023-01-01", weight=10.2, stature=75.7)
    .measured_at("2024-01-01", weight=12.6, stature=87.8)
    .build_and_calculate())

# Display and plot
print(patient.display_measurements())
plotter = Plotter(patient)
plotter.plot("weight", age_group="0-2", show=False, output_path="weight_chart.png")
""")

print("Lines of code: ~13")
print("Imports required: 2")
print("Intermediate objects: 1 (plotter)")
print("Code reduction: 41% fewer lines")
print("Pros: Self-documenting, validation at each step, readable")
print("Cons: Slightly more verbose than method chaining")


# =============================================================================
# Style 4: Unified Facade - Quick Patient
# =============================================================================

print("\n" + "=" * 80)
print("STYLE 4: Unified Facade - Quick Patient")
print("=" * 80)

print("""
# Single import
import pygrowthstandards as pgs

# Quick patient creation with all measurements
patient = pgs.quick_patient(
    sex="M",
    birthday="2022-01-01",
    measurements=[
        {"date": "2022-07-01", "weight": 8.6, "stature": 68.4},
        {"date": "2023-01-01", "weight": 10.2, "stature": 75.7},
        {"date": "2024-01-01", "weight": 12.6, "stature": 87.8}
    ]
)

# Calculate and display
patient.calculate_all()
print(patient.display_measurements())

# Plot
plotter = pgs.Plotter(patient)
plotter.plot("weight", age_group="0-2", show=False, output_path="weight_chart.png")
""")

print("Lines of code: ~15")
print("Imports required: 1")
print("Intermediate objects: 1 (plotter)")
print("Code reduction: 32% fewer lines")
print("Pros: Single import, data-driven, familiar dict structure")
print("Cons: Less fluent than method chaining")


# =============================================================================
# Style 5: Unified Facade - Builder via Facade
# =============================================================================

print("\n" + "=" * 80)
print("STYLE 5: Unified Facade - Builder")
print("=" * 80)

print("""
# Single import
import pygrowthstandards as pgs

# Use builder through facade
patient = (pgs.patient(sex="M", birthday="2022-01-01")
    .measured_at("2022-07-01", weight=8.6, stature=68.4)
    .measured_at("2023-01-01", weight=10.2, stature=75.7)
    .measured_at("2024-01-01", weight=12.6, stature=87.8)
    .build_and_calculate())

# Display and plot
print(patient.display_measurements())
plotter = pgs.Plotter(patient)
plotter.plot("weight", age_group="0-2", show=False, output_path="weight_chart.png")
""")

print("Lines of code: ~11")
print("Imports required: 1")
print("Intermediate objects: 1 (plotter)")
print("Code reduction: 50% fewer lines")
print("Pros: Single import, fluent interface, clean")
print("Cons: Slight learning curve for builder pattern")


# =============================================================================
# Summary Comparison Table
# =============================================================================

print("\n" + "=" * 80)
print("SUMMARY COMPARISON")
print("=" * 80)

comparison_data = """
| Style                | Lines | Imports | Reduction | Readability | Learning Curve |
|----------------------|-------|---------|-----------|-------------|----------------|
| 1. Current API       |   22  |    3    |     -     |   Medium    |     Low        |
| 2. Method Chaining   |    9  |    2    |    59%    |   High      |     Low        |
| 3. Builder Pattern   |   13  |    2    |    41%    |   High      |     Medium     |
| 4. Quick Patient     |   15  |    1    |    32%    |   Medium    |     Low        |
| 5. Facade + Builder  |   11  |    1    |    50%    |   High      |     Medium     |
"""

print(comparison_data)


# =============================================================================
# Additional Use Case: Simple One-off Calculation
# =============================================================================

print("\n" + "=" * 80)
print("USE CASE: Simple One-off Calculation")
print("=" * 80)

print("\nCurrent API:")
print("------------")
print("""
from pygrowthstandards import functional as F
z = F.zscore("weight", 10.5, "M", age_days=365)
""")

print("\nUnified Facade:")
print("---------------")
print("""
import pygrowthstandards as pgs
z = pgs.zscore("weight", 10.5, "M", age_days=365)
""")

print("\nResult: Slightly simpler import, same clarity")


# =============================================================================
# Additional Use Case: Batch Processing
# =============================================================================

print("\n" + "=" * 80)
print("USE CASE: Batch Processing (DataFrame)")
print("=" * 80)

print("\nCurrent API:")
print("------------")
print("""
from pygrowthstandards import functional as F
import pandas as pd

df = pd.DataFrame({...})

# Manual iteration
df['zscore'] = df.apply(
    lambda row: F.zscore(
        row['measurement'],
        row['value'],
        row['sex'],
        age_days=row['age_days']
    ),
    axis=1
)
""")

print("\nUnified Facade:")
print("---------------")
print("""
import pygrowthstandards as pgs
import pandas as pd

df = pd.DataFrame({...})

# Built-in batch processing
df = pgs.batch_calculate(
    df,
    measurement_col='measurement',
    value_col='value',
    sex_col='sex',
    age_days_col='age_days'
)
""")

print("\nResult: Much cleaner, purpose-built batch method")


# =============================================================================
# Recommendations
# =============================================================================

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

recommendations = """
Based on the comparison above, the recommended implementation strategy is:

1. **Phase 1** (High Priority - Immediate Impact):
   - Implement method chaining in existing Patient class
   - Add measured_at() convenience method
   - Integrate plot() directly into Patient
   - Expected: 50-60% code reduction for common workflows
   - Risk: Very low (backward compatible)

2. **Phase 2** (Medium Priority - Enhanced Flexibility):
   - Add PatientBuilder class for declarative construction
   - Provide validation at each step
   - Enable both imperative and declarative styles
   - Expected: Improved readability and self-documenting code
   - Risk: Low (additive only)

3. **Phase 3** (Low Priority - Simplified Access):
   - Create unified facade API (import pygrowthstandards as pgs)
   - Add convenience methods (quick_patient, batch_calculate)
   - Simplify imports and discovery
   - Expected: Lower barrier to entry for new users
   - Risk: Medium (requires careful namespace design)

All phases maintain 100% backward compatibility with existing code.

Benefits Summary:
- 40-60% reduction in code for common tasks
- Improved readability and maintainability
- Lower learning curve for new users
- Progressive disclosure of complexity
- Better IDE autocomplete support
"""

print(recommendations)


# =============================================================================
# Conclusion
# =============================================================================

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

print("""
The fluid API enhancements provide significant improvements in:

1. **Developer Experience**: Less boilerplate, more readable code
2. **Productivity**: Faster time from thought to working code
3. **Maintainability**: Self-documenting patterns, fewer intermediate objects
4. **Flexibility**: Multiple patterns for different use cases
5. **Backward Compatibility**: All existing code continues to work

The method chaining approach (Style 2) offers the best immediate ROI:
- Minimal implementation effort
- Maximum code reduction (59%)
- High readability
- Zero breaking changes

Recommendation: Start with Phase 1 (method chaining), then gather user
feedback before implementing subsequent phases.
""")

print("=" * 80)
print("End of comparison")
print("=" * 80)
