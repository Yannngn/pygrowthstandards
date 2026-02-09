# Research: Fluid API Design Patterns for PyGrowthStandards

**Date:** February 2026  
**Status:** Research Document  
**Purpose:** Evaluate and propose strategies for a flexible, fluid API system

---

## Executive Summary

This document presents research findings on modern Python API design patterns and proposes architectural approaches for enhancing PyGrowthStandards with a more fluid, flexible API system. The goal is to improve user experience while maintaining backward compatibility and accommodating diverse usage scenarios (functional API, OOP workflows, CLI, etc.).

### Key Recommendations

1. **Enhance Method Chaining**: Introduce fluent interfaces in the OOP API for patient data entry and calculations
2. **Builder Pattern**: Implement query builders for complex filtering and calculations
3. **Unified Entry Point**: Create a consolidated API surface with intelligent routing
4. **Backwards Compatibility**: Maintain current functional and OOP APIs while adding new patterns
5. **Performance**: Ensure lazy evaluation and efficient data handling

---

## Table of Contents

1. [Current API Analysis](#current-api-analysis)
2. [Modern Python API Design Patterns](#modern-python-api-design-patterns)
3. [Analysis of Similar Libraries](#analysis-of-similar-libraries)
4. [Proposed Architectures](#proposed-architectures)
5. [Prototype Examples](#prototype-examples)
6. [Tradeoffs Analysis](#tradeoffs-analysis)
7. [Recommendations](#recommendations)

---

## Current API Analysis

### Existing API Structure

PyGrowthStandards currently offers two primary API patterns:

#### 1. Functional API (Stateless)
```python
from pygrowthstandards import functional as F

# Direct, stateless calculations
z_score = F.zscore("weight", 5, "F", age_days=30)
percentile = F.percentile("stature", 75, "F", age_days=365)
```

**Strengths:**
- Simple and direct for one-off calculations
- No state management required
- Low cognitive overhead
- Fast for single operations

**Weaknesses:**
- Repetitive for multiple related calculations
- No context preservation between calls
- Limited composability
- Verbose for batch operations

#### 2. Object-Oriented API (Stateful)
```python
from pygrowthstandards import Patient, MeasurementGroup, Plotter

# Create patient and add measurements
patient = Patient(sex="M", birthday_date=datetime.date(2022, 1, 1))
patient.add_measurements(
    MeasurementGroup(date=datetime.date(2022, 7, 1), weight=8.6, stature=68.4)
)
patient.calculate_all()
print(patient.display_measurements())
```

**Strengths:**
- Natural for longitudinal tracking
- Maintains patient context
- Organized data structure
- Good for visualization workflows

**Weaknesses:**
- Imperative style requires multiple steps
- No method chaining support
- State mutation can be error-prone
- Limited fluent interface patterns

### Gap Analysis

The current API lacks:
1. **Fluent interfaces** for method chaining
2. **Builder patterns** for complex query construction
3. **Declarative syntax** for common workflows
4. **Lazy evaluation** for performance optimization
5. **Pipeline composition** for data transformations
6. **Unified entry point** for simplified access

---

## Modern Python API Design Patterns

### 1. Fluent Interfaces / Method Chaining

**Pattern:** Return `self` from methods to enable chaining.

**Example:**
```python
result = (calculator
    .add_measurement(weight=10.5, date="2023-01-01")
    .add_measurement(weight=11.2, date="2023-02-01")
    .calculate()
    .filter(metric="weight")
    .plot())
```

**Benefits:**
- Readable, declarative code
- Natural flow from left to right
- Reduces intermediate variables
- IDE autocomplete friendly

**Libraries using this:**
- pandas: `df.filter(...).groupby(...).mean()`
- SQLAlchemy: `query.filter(...).order_by(...).limit(...)`
- pytest: `pytest.raises(Exception).match("error")`

**Considerations:**
- Debug stack traces can be harder to read
- Requires careful return value design
- Mutation vs immutability decisions

### 2. Builder Pattern

**Pattern:** Separate construction from representation with a step-by-step builder.

**Example:**
```python
calculator = (GrowthCalculator()
    .for_patient(sex="M", birthday="2022-01-01")
    .with_measurements([
        {"date": "2022-07-01", "weight": 8.6, "stature": 68.4},
        {"date": "2023-01-01", "weight": 10.2, "stature": 75.7}
    ])
    .using_standard("WHO")
    .build())

results = calculator.calculate_all()
```

**Benefits:**
- Clear separation of concerns
- Validates incrementally
- Easy to extend with new options
- Immutable after building

**Libraries using this:**
- Pydantic: validation and settings management
- attrs/dataclasses: structured configuration
- scikit-learn pipelines: `Pipeline([...]).fit()`

**Considerations:**
- Adds abstraction layer
- Slight performance overhead
- May be overkill for simple use cases

### 3. Context Manager Pattern

**Pattern:** Use `with` statements for resource management and scoped operations.

**Example:**
```python
with GrowthAnalysis(patient) as analysis:
    analysis.add_measurements(measurements)
    analysis.calculate()
    charts = analysis.generate_charts()
    # Automatic cleanup and validation on exit
```

**Benefits:**
- Automatic resource management
- Clear scope boundaries
- Exception safety
- Pythonic idiom

**Libraries using this:**
- pandas: file I/O with automatic closing
- matplotlib: figure management
- tempfile: automatic cleanup

**Considerations:**
- May be unnecessary for stateless operations
- Adds boilerplate for simple cases

### 4. Query Builder / DSL Pattern

**Pattern:** Domain-specific language for constructing complex queries.

**Example:**
```python
from pygrowthstandards.query import Q

results = (calculator
    .select("weight", "stature", "head_circumference")
    .where(Q.age.between(0, 730))
    .and_where(Q.sex == "M")
    .calculate(method="zscore")
    .to_dataframe())
```

**Benefits:**
- Highly expressive for complex queries
- Type-safe with proper implementation
- Natural language-like syntax
- Composable query parts

**Libraries using this:**
- Django ORM: `Model.objects.filter(...)`
- SQLAlchemy: query construction
- pandas: query method with string expressions

**Considerations:**
- Significant implementation complexity
- Learning curve for users
- Potential performance implications

### 5. Pipeline / Compose Pattern

**Pattern:** Chain transformations in a functional style.

**Example:**
```python
from pygrowthstandards.pipeline import Pipeline

pipeline = Pipeline([
    LoadMeasurements(),
    CalculateZScores(standard="WHO"),
    FilterOutliers(threshold=3),
    GeneratePercentiles(),
    PlotGrowthCurves()
])

results = pipeline.execute(patient_data)
```

**Benefits:**
- Testable individual components
- Reusable transformation steps
- Clear data flow
- Parallelization opportunities

**Libraries using this:**
- scikit-learn: `Pipeline` for ML workflows
- Apache Beam / Dask: distributed pipelines
- functools: `reduce`, composition

**Considerations:**
- May be too abstract for simple cases
- Debugging can be challenging
- Overhead for simple operations

### 6. Facade / Unified Entry Point Pattern

**Pattern:** Single, simplified interface to complex subsystems.

**Example:**
```python
import pygrowthstandards as pgs

# Automatic routing to appropriate API
result = pgs.calculate("weight", 10.5, sex="M", age_days=365)

# Or with explicit patient context
patient = pgs.create_patient(sex="M", birthday="2022-01-01")
result = pgs.calculate(patient, measurement="weight", value=10.5)
```

**Benefits:**
- Lower barrier to entry
- Reduced imports
- Consistent interface
- Discovery through single namespace

**Libraries using this:**
- NumPy: `np.*` for array operations
- requests: simple HTTP interface
- pathlib: unified path operations

**Considerations:**
- Can hide complexity
- May limit advanced use cases
- Namespace pollution concerns

---

## Analysis of Similar Libraries

### pandas: The Gold Standard for Fluent Data APIs

**Key Patterns:**
1. **Method Chaining**: `df.filter().groupby().agg()`
2. **Flexible Input**: Multiple ways to achieve same result
3. **Lazy Evaluation**: Some operations defer computation
4. **Rich Accessor API**: `df.str.*`, `df.dt.*` for domain-specific operations

**Relevant Features for PyGrowthStandards:**
```python
# pandas-inspired growth API
patient_data = (pgs.DataFrame(measurements)
    .with_patient(sex="M", birthday="2022-01-01")
    .calculate_zscores()
    .filter(lambda x: x.age_days < 730)
    .plot.growth_chart())
```

**Lessons:**
- Method chaining is essential for data workflows
- Provide both functional and method-based APIs
- Accessors (`pgs.Patient.growth.*`) for domain-specific operations
- Balance flexibility with discoverability

### scikit-learn: Consistent Estimator API

**Key Patterns:**
1. **Consistent Interface**: `fit()`, `transform()`, `predict()`
2. **Pipeline Composition**: Chainable transformers
3. **Hyperparameter Access**: `get_params()`, `set_params()`
4. **Cloning**: Immutable patterns with `clone()`

**Relevant Features for PyGrowthStandards:**
```python
# scikit-learn inspired calculator
calculator = GrowthCalculator(standard="WHO", method="zscore")
calculator.fit(patient)  # Learn patient context
results = calculator.transform(measurements)  # Apply calculations

# Or in pipeline
pipeline = make_pipeline(
    GrowthCalculator(standard="WHO"),
    OutlierFilter(threshold=3),
    PercentileCalculator()
)
results = pipeline.fit_transform(patient_data)
```

**Lessons:**
- Consistency across API reduces cognitive load
- Composition enables complex workflows
- Separation of configuration and execution
- Immutability where possible

### statsmodels: Statistical Modeling API

**Key Patterns:**
1. **Formula Interface**: R-style formulas for models
2. **Result Objects**: Rich objects with multiple outputs
3. **Summary Methods**: Comprehensive reporting
4. **Multiple Representations**: LaTeX, HTML, text

**Relevant Features for PyGrowthStandards:**
```python
# statsmodels-inspired formula interface
results = pgs.growth("zscore ~ weight + stature | patient_sex + age_days", 
                     data=measurements)
results.summary()
results.plot()
results.to_latex()
```

**Lessons:**
- Formula interfaces powerful for statistical operations
- Rich result objects encapsulate complex outputs
- Multiple output formats increase utility
- Documentation integrated with results

### requests: Simplicity-First Design

**Key Patterns:**
1. **Minimal Required Arguments**: Sensible defaults
2. **Kwargs for Options**: `requests.get(url, timeout=5, headers={...})`
3. **Session Objects**: Stateful vs stateless options
4. **Response Objects**: Rich, self-documenting results

**Relevant Features for PyGrowthStandards:**
```python
# requests-inspired simple API
result = pgs.zscore("weight", 10.5, sex="M", age_days=365)

# Or with session for multiple calculations
with pgs.Session(patient_context) as session:
    r1 = session.zscore("weight", 10.5)
    r2 = session.zscore("stature", 75)
    r3 = session.percentile("weight", 10.5)
```

**Lessons:**
- Simplicity attracts users
- Progressive disclosure of complexity
- Both stateless and stateful options
- Self-documenting return values

---

## Proposed Architectures

### Architecture 1: Enhanced Current API (Minimal Changes)

**Description:** Add fluent interface methods to existing classes without breaking changes.

**Implementation:**
```python
class Patient:
    def add_measurement(self, measurement):
        """Add single measurement (existing behavior)."""
        # ... existing code ...
        return self  # NEW: Return self for chaining
    
    def add_measurements(self, measurements):
        """Add multiple measurements."""
        # ... existing code ...
        return self  # NEW: Return self for chaining
    
    def calculate_all(self):
        """Calculate all z-scores."""
        # ... existing code ...
        return self  # NEW: Return self for chaining
    
    def plot(self, measurement_type, **kwargs):
        """NEW: Direct plotting method."""
        plotter = Plotter(self)
        return plotter.plot(measurement_type=measurement_type, **kwargs)

# Usage
(Patient(sex="M", birthday_date="2022-01-01")
    .add_measurements(MeasurementGroup(...))
    .add_measurements(MeasurementGroup(...))
    .calculate_all()
    .plot("weight", age_group="0-2"))
```

**Pros:**
- Minimal breaking changes
- Easy to implement
- Maintains backward compatibility
- Low risk

**Cons:**
- Limited improvement to API expressiveness
- Doesn't address all pain points
- Still imperative style

### Architecture 2: Builder Pattern with Immutability

**Description:** Introduce builder classes for constructing patients and calculations.

**Implementation:**
```python
class PatientBuilder:
    def __init__(self):
        self._sex = None
        self._birthday = None
        self._gestational_age = 40
        self._measurements = []
    
    def with_sex(self, sex):
        """Set patient sex."""
        self._sex = sex
        return self
    
    def born_on(self, date):
        """Set birthday."""
        self._birthday = date
        return self
    
    def gestational_age(self, weeks, days=0):
        """Set gestational age."""
        self._gestational_age = weeks * 7 + days
        return self
    
    def measured_at(self, date, **measurements):
        """Add measurements at a specific date."""
        self._measurements.append(
            MeasurementGroup(date=date, **measurements)
        )
        return self
    
    def build(self):
        """Create Patient instance."""
        patient = Patient(
            sex=self._sex,
            birthday_date=self._birthday,
            gestational_age_weeks=self._gestational_age // 7
        )
        for m in self._measurements:
            patient.add_measurements(m)
        return patient

# Usage
patient = (PatientBuilder()
    .with_sex("M")
    .born_on(datetime.date(2022, 1, 1))
    .measured_at(datetime.date(2022, 7, 1), weight=8.6, stature=68.4)
    .measured_at(datetime.date(2023, 1, 1), weight=10.2, stature=75.7)
    .build())

patient.calculate_all()
```

**Pros:**
- Clear construction process
- Validation at each step
- Immutable after building
- No breaking changes

**Cons:**
- Additional abstraction layer
- More classes to maintain
- Learning curve for users

### Architecture 3: Unified Facade with Smart Routing

**Description:** Single entry point that intelligently routes to appropriate implementation.

**Implementation:**
```python
# In __init__.py
class GrowthAPI:
    """Unified API facade for PyGrowthStandards."""
    
    @staticmethod
    def calculate(measurement, value, sex=None, age_days=None, 
                  patient=None, method="zscore", **kwargs):
        """
        Universal calculation method with smart routing.
        
        Can work with:
        - Individual values (functional style)
        - Patient objects (OOP style)
        - Dataframes (batch style)
        """
        if patient is not None:
            # Route to OOP calculator
            return patient.calculator.calculate_z_score(...)
        elif isinstance(value, pd.DataFrame):
            # Route to batch calculator
            return batch_calculate(...)
        else:
            # Route to functional API
            if method == "zscore":
                return functional.zscore(measurement, value, sex, age_days, **kwargs)
            elif method == "percentile":
                return functional.percentile(measurement, value, sex, age_days, **kwargs)
    
    @staticmethod
    def patient(sex, birthday=None, **kwargs):
        """Create a patient with fluent interface."""
        return FluentPatient(sex, birthday, **kwargs)
    
    @staticmethod  
    def batch(data):
        """Process batch of measurements."""
        return BatchCalculator(data)

# Usage - multiple styles
import pygrowthstandards as pgs

# Style 1: Simple functional
z = pgs.calculate("weight", 10.5, sex="M", age_days=365)

# Style 2: Fluent patient
patient = (pgs.patient(sex="M", birthday="2022-01-01")
    .add(date="2022-07-01", weight=8.6, stature=68.4)
    .add(date="2023-01-01", weight=10.2, stature=75.7)
    .calculate()
    .plot("weight"))

# Style 3: Batch processing
results = pgs.batch(df_measurements).calculate("zscore").to_dataframe()
```

**Pros:**
- Single import for everything
- Intuitive entry point
- Supports multiple paradigms
- Discoverable API

**Cons:**
- Complex internal routing logic
- Potential namespace conflicts
- Harder to maintain
- May hide important distinctions

### Architecture 4: Pipeline Composition System

**Description:** Functional pipeline for composing growth calculations.

**Implementation:**
```python
from pygrowthstandards.pipeline import Pipeline, ops

# Define reusable operations
load_patient = ops.LoadPatient(sex="M", birthday="2022-01-01")
add_measurements = ops.AddMeasurements([
    {"date": "2022-07-01", "weight": 8.6, "stature": 68.4},
    {"date": "2023-01-01", "weight": 10.2, "stature": 75.7}
])
calculate_zscores = ops.CalculateZScores(method="zscore")
filter_outliers = ops.FilterOutliers(threshold=3)
generate_plot = ops.GeneratePlot(measurement="weight", age_group="0-2")

# Compose pipeline
pipeline = Pipeline([
    load_patient,
    add_measurements,
    calculate_zscores,
    filter_outliers,
    generate_plot
])

# Execute
result = pipeline.execute()

# Or use operator overloading
result = (load_patient 
    >> add_measurements 
    >> calculate_zscores 
    >> filter_outliers 
    >> generate_plot)()
```

**Pros:**
- Highly testable components
- Reusable operations
- Clear data flow
- Functional programming style

**Cons:**
- Significant implementation effort
- Steeper learning curve
- May be overkill for simple cases
- Debugging complexity

### Architecture 5: Hybrid Approach (Recommended)

**Description:** Combine the best of multiple patterns for maximum flexibility.

**Implementation:**
```python
# Layer 1: Keep existing functional API (no changes)
from pygrowthstandards import functional as F
z = F.zscore("weight", 10.5, "M", age_days=365)

# Layer 2: Enhanced OOP with method chaining
from pygrowthstandards import Patient, MeasurementGroup

patient = (Patient(sex="M", birthday_date=datetime.date(2022, 1, 1))
    .add_measurements(MeasurementGroup(date=..., weight=8.6, stature=68.4))
    .calculate_all()
    .display_measurements())

# Layer 3: Fluent builder for complex construction
from pygrowthstandards.builders import PatientBuilder

patient = (PatientBuilder()
    .with_sex("M")
    .born_on("2022-01-01")
    .measured_at("2022-07-01", weight=8.6, stature=68.4)
    .measured_at("2023-01-01", weight=10.2, stature=75.7)
    .build_and_calculate())

# Layer 4: Convenient facade for common operations
import pygrowthstandards as pgs

# Quick calculation
z = pgs.calculate("weight", 10.5, sex="M", age_days=365)

# Quick patient with fluent interface
patient = pgs.quick_patient(
    sex="M", 
    birthday="2022-01-01",
    measurements=[
        {"date": "2022-07-01", "weight": 8.6, "stature": 68.4},
        {"date": "2023-01-01", "weight": 10.2, "stature": 75.7}
    ]
).calculate_all().plot("weight")

# Layer 5: Batch processing for DataFrames
results_df = pgs.batch_calculate(
    df,
    measurement_col="weight",
    age_col="age_days",
    sex_col="sex"
)
```

**Pros:**
- Progressive disclosure of complexity
- Maintains backward compatibility
- Multiple entry points for different users
- Best of all patterns

**Cons:**
- Most complex to implement
- Requires comprehensive documentation
- Larger codebase to maintain

---

## Prototype Examples

### Example 1: Enhanced Patient with Method Chaining

```python
# File: src/pygrowthstandards/oop/fluent_patient.py

import datetime
from typing import Any

from .patient import Patient
from .measurement import MeasurementGroup


class FluentPatient(Patient):
    """
    Enhanced Patient class with fluent interface support.
    
    Maintains backward compatibility while enabling method chaining.
    """
    
    def add_measurement(self, measurement) -> "FluentPatient":
        """Add single measurement and return self for chaining."""
        super().add_measurement(measurement)
        return self
    
    def add_measurements(self, measurements) -> "FluentPatient":
        """Add measurement group and return self for chaining."""
        super().add_measurements(measurements)
        return self
    
    def calculate_all(self) -> "FluentPatient":
        """Calculate all z-scores and return self for chaining."""
        super().calculate_all()
        return self
    
    def measured_at(self, date: datetime.date, **measurements: float) -> "FluentPatient":
        """
        Convenient method to add measurements at a specific date.
        
        Args:
            date: Date of measurement
            **measurements: Measurement values (weight, stature, etc.)
        
        Returns:
            Self for chaining
        
        Example:
            patient.measured_at(
                datetime.date(2022, 7, 1),
                weight=8.6,
                stature=68.4
            )
        """
        group = MeasurementGroup(date=date, **measurements)
        self.add_measurements(group)
        return self
    
    def plot(self, measurement_type: str, age_group: str | None = None, 
             **kwargs: Any) -> "FluentPatient":
        """
        Plot growth chart and return self for chaining.
        
        Args:
            measurement_type: Type of measurement to plot
            age_group: Age group for chart (optional)
            **kwargs: Additional plotting options
        
        Returns:
            Self for chaining
        """
        from .plotter import Plotter
        plotter = Plotter(self)
        plotter.plot(
            measurement_type=measurement_type,
            age_group=age_group or self._infer_age_group(),
            **kwargs
        )
        return self
    
    def filter(self, **criteria: Any) -> "FluentPatient":
        """
        Filter measurements based on criteria.
        
        Args:
            **criteria: Filtering conditions
        
        Returns:
            New FluentPatient with filtered measurements
        
        Example:
            filtered = patient.filter(
                date_after=datetime.date(2022, 6, 1),
                weight_min=8.0
            )
        """
        # Implementation would filter measurements
        # For now, return self for chaining
        # TODO: Implement actual filtering logic
        return self
    
    def _infer_age_group(self) -> str:
        """Infer appropriate age group from patient's current age."""
        if not self.measurements:
            return "0-2"
        
        latest_date = max(m.date for m in self.measurements)
        age_days = self.age(latest_date).days
        
        if age_days <= 730:
            return "0-2"
        elif age_days <= 1825:
            return "2-5"
        elif age_days <= 3650:
            return "5-10"
        else:
            return "10-19"


# Usage example
if __name__ == "__main__":
    patient = (FluentPatient(sex="M", birthday_date=datetime.date(2022, 1, 1))
        .measured_at(datetime.date(2022, 7, 1), weight=8.6, stature=68.4)
        .measured_at(datetime.date(2023, 1, 1), weight=10.2, stature=75.7)
        .measured_at(datetime.date(2024, 1, 1), weight=12.6, stature=87.8)
        .calculate_all()
        .plot("weight", show=False, output_path="growth_chart.png"))
    
    print(patient.display_measurements())
```

### Example 2: Builder Pattern Implementation

```python
# File: src/pygrowthstandards/builders/patient_builder.py

import datetime
from typing import Any, Dict, List

from ..oop.patient import Patient
from ..oop.measurement import MeasurementGroup


class PatientBuilder:
    """
    Builder for constructing Patient objects with a fluent interface.
    
    This builder provides a declarative way to construct patients with
    validation at each step.
    """
    
    def __init__(self):
        self._sex: str | None = None
        self._birthday: datetime.date | None = None
        self._gestational_age_weeks: int = 40
        self._gestational_age_days: int = 0
        self._measurements: List[Dict[str, Any]] = []
    
    def with_sex(self, sex: str) -> "PatientBuilder":
        """
        Set patient sex.
        
        Args:
            sex: "M", "F", or "U"
        
        Returns:
            Self for chaining
        """
        if sex not in ["M", "F", "U"]:
            raise ValueError(f"Invalid sex: {sex}. Must be 'M', 'F', or 'U'")
        self._sex = sex
        return self
    
    def male(self) -> "PatientBuilder":
        """Convenience method to set sex to male."""
        return self.with_sex("M")
    
    def female(self) -> "PatientBuilder":
        """Convenience method to set sex to female."""
        return self.with_sex("F")
    
    def born_on(self, date: datetime.date | str) -> "PatientBuilder":
        """
        Set birthday.
        
        Args:
            date: Birthday as date object or ISO string
        
        Returns:
            Self for chaining
        """
        if isinstance(date, str):
            date = datetime.date.fromisoformat(date)
        self._birthday = date
        return self
    
    def gestational_age(self, weeks: int, days: int = 0) -> "PatientBuilder":
        """
        Set gestational age.
        
        Args:
            weeks: Gestational age in weeks
            days: Additional days
        
        Returns:
            Self for chaining
        """
        self._gestational_age_weeks = weeks
        self._gestational_age_days = days
        return self
    
    def preterm(self, weeks: int = 35) -> "PatientBuilder":
        """Convenience method for preterm infants."""
        return self.gestational_age(weeks)
    
    def measured_at(self, date: datetime.date | str, 
                    **measurements: float) -> "PatientBuilder":
        """
        Add measurements at a specific date.
        
        Args:
            date: Measurement date
            **measurements: Measurement values
        
        Returns:
            Self for chaining
        """
        if isinstance(date, str):
            date = datetime.date.fromisoformat(date)
        
        self._measurements.append({
            "date": date,
            **measurements
        })
        return self
    
    def with_measurements(self, measurements: List[Dict[str, Any]]) -> "PatientBuilder":
        """
        Add multiple measurements at once.
        
        Args:
            measurements: List of measurement dictionaries
        
        Returns:
            Self for chaining
        """
        for m in measurements:
            date = m.get("date")
            if isinstance(date, str):
                date = datetime.date.fromisoformat(date)
            
            measurement_data = {k: v for k, v in m.items() if k != "date"}
            self._measurements.append({
                "date": date,
                **measurement_data
            })
        return self
    
    def validate(self) -> None:
        """Validate builder state before building."""
        if self._sex is None:
            raise ValueError("Sex must be set before building")
        
        if self._birthday is None and self._measurements:
            raise ValueError("Birthday required when measurements are provided")
    
    def build(self) -> Patient:
        """
        Build and return Patient instance.
        
        Returns:
            Configured Patient object
        """
        self.validate()
        
        patient = Patient(
            sex=self._sex,
            birthday_date=self._birthday,
            gestational_age_weeks=self._gestational_age_weeks,
            gestational_age_days=self._gestational_age_days
        )
        
        for m in self._measurements:
            date = m["date"]
            measurement_data = {k: v for k, v in m.items() if k != "date"}
            patient.add_measurements(
                MeasurementGroup(date=date, **measurement_data)
            )
        
        return patient
    
    def build_and_calculate(self) -> Patient:
        """
        Build patient and immediately calculate all z-scores.
        
        Returns:
            Patient with calculated z-scores
        """
        patient = self.build()
        patient.calculate_all()
        return patient


# Usage example
if __name__ == "__main__":
    patient = (PatientBuilder()
        .male()
        .born_on("2022-01-01")
        .preterm(weeks=36)
        .measured_at("2022-07-01", weight=8.6, stature=68.4)
        .measured_at("2023-01-01", weight=10.2, stature=75.7)
        .measured_at("2024-01-01", weight=12.6, stature=87.8)
        .build_and_calculate())
    
    print(patient.display_measurements())
```

### Example 3: Unified Facade API

```python
# File: src/pygrowthstandards/api.py

"""
Unified facade API for PyGrowthStandards.

Provides a single entry point for all common operations with intelligent
routing to the appropriate underlying implementation.
"""

import datetime
from typing import Any, Dict, List, Union

import pandas as pd

from . import functional
from .oop import Patient, MeasurementGroup
from .builders.patient_builder import PatientBuilder


class API:
    """Unified API facade for PyGrowthStandards."""
    
    @staticmethod
    def calculate(measurement: str, 
                  value: float,
                  sex: str = "U",
                  age_days: int | None = None,
                  gestational_age: int | None = None,
                  method: str = "zscore",
                  **kwargs: Any) -> float:
        """
        Calculate z-score or percentile for a measurement.
        
        Args:
            measurement: Measurement type (e.g., "weight", "stature")
            value: Measurement value
            sex: Patient sex ("M", "F", or "U")
            age_days: Age in days (for postnatal)
            gestational_age: Gestational age in days (for prenatal/newborn)
            method: "zscore" or "percentile"
            **kwargs: Additional options
        
        Returns:
            Calculated z-score or percentile
        
        Example:
            >>> import pygrowthstandards as pgs
            >>> z = pgs.calculate("weight", 10.5, sex="M", age_days=365)
            >>> p = pgs.calculate("stature", 75, sex="F", age_days=365, method="percentile")
        """
        if method == "zscore":
            return functional.zscore(
                measurement, value, sex, age_days, gestational_age, **kwargs
            )
        elif method == "percentile":
            return functional.percentile(
                measurement, value, sex, age_days, gestational_age, **kwargs
            )
        else:
            raise ValueError(f"Unknown method: {method}")
    
    @staticmethod
    def zscore(measurement: str, value: float, sex: str = "U",
               age_days: int | None = None,
               gestational_age: int | None = None) -> float:
        """Convenience method for z-score calculation."""
        return functional.zscore(measurement, value, sex, age_days, gestational_age)
    
    @staticmethod
    def percentile(measurement: str, value: float, sex: str = "U",
                   age_days: int | None = None,
                   gestational_age: int | None = None) -> float:
        """Convenience method for percentile calculation."""
        return functional.percentile(measurement, value, sex, age_days, gestational_age)
    
    @staticmethod
    def patient(sex: str,
                birthday: datetime.date | str | None = None,
                gestational_age_weeks: int = 40,
                **kwargs: Any) -> PatientBuilder:
        """
        Create a patient using the builder pattern.
        
        Args:
            sex: Patient sex ("M", "F", or "U")
            birthday: Birthday date
            gestational_age_weeks: Gestational age in weeks
            **kwargs: Additional patient parameters
        
        Returns:
            PatientBuilder for fluent construction
        
        Example:
            >>> patient = (pgs.patient(sex="M", birthday="2022-01-01")
            ...     .measured_at("2022-07-01", weight=8.6, stature=68.4)
            ...     .build_and_calculate())
        """
        builder = PatientBuilder().with_sex(sex)
        
        if birthday:
            if isinstance(birthday, str):
                birthday = datetime.date.fromisoformat(birthday)
            builder = builder.born_on(birthday)
        
        if gestational_age_weeks != 40:
            builder = builder.gestational_age(gestational_age_weeks)
        
        return builder
    
    @staticmethod
    def quick_patient(sex: str,
                      birthday: datetime.date | str,
                      measurements: List[Dict[str, Any]],
                      gestational_age_weeks: int = 40) -> Patient:
        """
        Quickly create a patient with measurements.
        
        Args:
            sex: Patient sex
            birthday: Birthday date
            measurements: List of measurement dictionaries
            gestational_age_weeks: Gestational age in weeks
        
        Returns:
            Patient object with measurements added
        
        Example:
            >>> patient = pgs.quick_patient(
            ...     sex="M",
            ...     birthday="2022-01-01",
            ...     measurements=[
            ...         {"date": "2022-07-01", "weight": 8.6, "stature": 68.4},
            ...         {"date": "2023-01-01", "weight": 10.2, "stature": 75.7}
            ...     ]
            ... )
        """
        return (API.patient(sex, birthday, gestational_age_weeks)
            .with_measurements(measurements)
            .build())
    
    @staticmethod
    def batch_calculate(data: pd.DataFrame,
                        measurement_col: str,
                        value_col: str,
                        sex_col: str,
                        age_days_col: str | None = None,
                        gestational_age_col: str | None = None,
                        method: str = "zscore") -> pd.DataFrame:
        """
        Calculate z-scores or percentiles for a batch of measurements.
        
        Args:
            data: DataFrame with measurement data
            measurement_col: Column with measurement types
            value_col: Column with measurement values
            sex_col: Column with sex values
            age_days_col: Column with age in days
            gestational_age_col: Column with gestational age
            method: "zscore" or "percentile"
        
        Returns:
            DataFrame with calculated values added
        
        Example:
            >>> df = pd.DataFrame({
            ...     "measurement": ["weight", "stature"],
            ...     "value": [10.5, 75],
            ...     "sex": ["M", "F"],
            ...     "age_days": [365, 365]
            ... })
            >>> results = pgs.batch_calculate(
            ...     df,
            ...     measurement_col="measurement",
            ...     value_col="value",
            ...     sex_col="sex",
            ...     age_days_col="age_days"
            ... )
        """
        result_col = f"{method}_result"
        
        def calculate_row(row):
            return API.calculate(
                measurement=row[measurement_col],
                value=row[value_col],
                sex=row[sex_col],
                age_days=row[age_days_col] if age_days_col else None,
                gestational_age=row[gestational_age_col] if gestational_age_col else None,
                method=method
            )
        
        data[result_col] = data.apply(calculate_row, axis=1)
        return data


# Singleton instance for module-level access
_api = API()

# Module-level functions that delegate to API
calculate = _api.calculate
zscore = _api.zscore
percentile = _api.percentile
patient = _api.patient
quick_patient = _api.quick_patient
batch_calculate = _api.batch_calculate

__all__ = [
    "API",
    "calculate",
    "zscore",
    "percentile",
    "patient",
    "quick_patient",
    "batch_calculate"
]
```

### Example 4: Usage Comparison

```python
"""
Comparison of different API styles for the same task.
"""

import datetime
import pygrowthstandards as pgs

# =============================================================================
# Task: Create a male patient born on 2022-01-01, add measurements over time,
#       calculate z-scores, and generate a growth chart
# =============================================================================

# -----------------------------------------------------------------------------
# Current API (v0.1.3)
# -----------------------------------------------------------------------------
patient_old = pgs.Patient(
    sex="M",
    birthday_date=datetime.date(2022, 1, 1)
)

patient_old.add_measurements(
    pgs.MeasurementGroup(date=datetime.date(2022, 7, 1), weight=8.6, stature=68.4)
)
patient_old.add_measurements(
    pgs.MeasurementGroup(date=datetime.date(2023, 1, 1), weight=10.2, stature=75.7)
)
patient_old.add_measurements(
    pgs.MeasurementGroup(date=datetime.date(2024, 1, 1), weight=12.6, stature=87.8)
)

patient_old.calculate_all()
print(patient_old.display_measurements())

plotter_old = pgs.Plotter(patient_old)
plotter_old.plot(
    age_group="0-2",
    measurement_type="weight",
    show=False,
    output_path="weight_chart_old.png"
)

# -----------------------------------------------------------------------------
# Enhanced OOP with Method Chaining
# -----------------------------------------------------------------------------
from pygrowthstandards.oop import FluentPatient

patient_fluent = (FluentPatient(sex="M", birthday_date=datetime.date(2022, 1, 1))
    .measured_at(datetime.date(2022, 7, 1), weight=8.6, stature=68.4)
    .measured_at(datetime.date(2023, 1, 1), weight=10.2, stature=75.7)
    .measured_at(datetime.date(2024, 1, 1), weight=12.6, stature=87.8)
    .calculate_all()
    .plot("weight", age_group="0-2", show=False, output_path="weight_chart_fluent.png"))

print(patient_fluent.display_measurements())

# -----------------------------------------------------------------------------
# Builder Pattern
# -----------------------------------------------------------------------------
from pygrowthstandards.builders import PatientBuilder

patient_builder = (PatientBuilder()
    .male()
    .born_on("2022-01-01")
    .measured_at("2022-07-01", weight=8.6, stature=68.4)
    .measured_at("2023-01-01", weight=10.2, stature=75.7)
    .measured_at("2024-01-01", weight=12.6, stature=87.8)
    .build_and_calculate())

print(patient_builder.display_measurements())

plotter_builder = pgs.Plotter(patient_builder)
plotter_builder.plot(
    age_group="0-2",
    measurement_type="weight",
    show=False,
    output_path="weight_chart_builder.png"
)

# -----------------------------------------------------------------------------
# Unified Facade API
# -----------------------------------------------------------------------------
patient_facade = pgs.quick_patient(
    sex="M",
    birthday="2022-01-01",
    measurements=[
        {"date": datetime.date(2022, 7, 1), "weight": 8.6, "stature": 68.4},
        {"date": datetime.date(2023, 1, 1), "weight": 10.2, "stature": 75.7},
        {"date": datetime.date(2024, 1, 1), "weight": 12.6, "stature": 87.8}
    ]
)

patient_facade.calculate_all()
print(patient_facade.display_measurements())

# Or even more concise
patient_compact = (pgs.patient(sex="M", birthday="2022-01-01")
    .measured_at("2022-07-01", weight=8.6, stature=68.4)
    .measured_at("2023-01-01", weight=10.2, stature=75.7)
    .measured_at("2024-01-01", weight=12.6, stature=87.8)
    .build_and_calculate())

# -----------------------------------------------------------------------------
# Line Count Comparison
# -----------------------------------------------------------------------------
# Current API:      ~20 lines
# Method Chaining:  ~7 lines (65% reduction)
# Builder Pattern:  ~10 lines (50% reduction)
# Facade API:       ~7-14 lines (30-65% reduction)
```

---

## Tradeoffs Analysis

### Implementation Complexity vs User Experience

| Pattern | Impl. Complexity | User Learning | Code Reduction | Maint. Burden |
|---------|------------------|---------------|----------------|---------------|
| Method Chaining | Low | Low | 30-50% | Low |
| Builder Pattern | Medium | Medium | 40-60% | Medium |
| Unified Facade | High | Low | 50-70% | High |
| Pipeline | Very High | High | Variable | Very High |
| Hybrid | High | Medium | 40-65% | High |

### Performance Considerations

1. **Method Chaining**: 
   - No performance overhead
   - Same operations as current API
   - Just different syntax

2. **Builder Pattern**:
   - Slight memory overhead for builder state
   - Validation at each step adds minimal cost
   - Build step is one-time cost

3. **Unified Facade**:
   - Routing logic adds minimal overhead
   - Smart detection may slow edge cases
   - Generally negligible for typical use

4. **Pipeline**:
   - Potential for lazy evaluation benefits
   - Overhead of abstraction layers
   - Opportunity for optimization

### Backward Compatibility

| Pattern | Breaking Changes | Migration Path | Coexistence |
|---------|------------------|----------------|-------------|
| Method Chaining | None | Optional upgrade | Perfect |
| Builder Pattern | None | Additive only | Perfect |
| Unified Facade | None | Import changes only | Perfect |
| Pipeline | None | New module | Perfect |
| Hybrid | None | Progressive adoption | Perfect |

### Maintenance Impact

**Positive:**
- More testable with smaller components
- Clearer separation of concerns
- Easier to extend

**Negative:**
- More code to maintain
- Documentation overhead
- Potential for confusion with multiple patterns

### Ecosystem Alignment

Alignment with Python ecosystem best practices:

✅ **Pythonic idioms**: Method chaining, context managers, iterators  
✅ **Type hints**: Full type annotation support  
✅ **IDE support**: Better autocomplete with fluent interfaces  
✅ **PEP 8**: Follows style guidelines  
✅ **Duck typing**: Compatible with existing patterns  

---

## Recommendations

### Phased Implementation Plan

#### Phase 1: Low-Risk Enhancements (Recommended for v0.2.0)

**Implement Method Chaining in Existing Classes**

1. Modify `Patient`, `MeasurementGroup`, `Calculator` to return `self`
2. Add convenience methods (`measured_at()`, `plot()`)
3. 100% backward compatible
4. Immediate UX improvement

**Estimated effort:** 1-2 weeks  
**Risk:** Very Low  
**User Impact:** High (immediate productivity boost)

```python
# Example changes to Patient class
class Patient:
    def add_measurements(self, measurements):
        self.measurements.append(measurements)
        return self  # ADD THIS LINE
```

#### Phase 2: Builder Pattern (Optional, v0.3.0)

**Add Builder Classes for Complex Construction**

1. Create `PatientBuilder`, `MeasurementBuilder`
2. Provide declarative construction API
3. Add validation at each step
4. Fully coexists with current API

**Estimated effort:** 2-3 weeks  
**Risk:** Low  
**User Impact:** Medium (alternative API for power users)

#### Phase 3: Unified Facade (Optional, v0.4.0)

**Create Convenience API Layer**

1. Implement `API` facade class
2. Add module-level convenience functions
3. Smart routing between implementations
4. Simplify imports

**Estimated effort:** 3-4 weeks  
**Risk:** Medium  
**User Impact:** High (lower barrier to entry)

#### Phase 4: Advanced Features (Future)

**Pipeline, Batch Processing, Advanced Querying**

1. Evaluate demand from user feedback
2. Implement only if clear use cases emerge
3. Consider performance optimizations

**Estimated effort:** 6-8 weeks  
**Risk:** High  
**User Impact:** Variable (depends on use cases)

### Immediate Action Items

1. **Implement Phase 1** (Method Chaining)
   - Minimal risk, maximum immediate benefit
   - Sets foundation for future enhancements
   - Can be done incrementally

2. **Update Documentation**
   - Add fluent interface examples to README
   - Create API design guide
   - Document patterns and best practices

3. **Gather User Feedback**
   - Create GitHub discussion for API design
   - Survey users on pain points
   - Validate assumptions with real use cases

4. **Create Prototypes**
   - Implement prototypes for Phases 1-2
   - Get community feedback before final implementation
   - Iterate based on real-world usage

### Success Metrics

Track the following to measure API improvements:

- **Code Reduction**: % fewer lines for common tasks
- **Time to First Result**: Time for new users to get working code
- **API Satisfaction**: User surveys and feedback
- **Adoption Rate**: Usage of new vs old patterns
- **Issue Reduction**: Fewer "how do I..." questions

---

## Conclusion

PyGrowthStandards has a solid foundation with its dual functional and OOP APIs. The proposed fluid API enhancements, particularly **method chaining** and **builder patterns**, can significantly improve user experience without breaking existing code.

### Key Takeaways

1. **Start with method chaining** - lowest risk, highest immediate impact
2. **Maintain backward compatibility** - all enhancements should be additive
3. **Progressive disclosure** - simple things simple, complex things possible
4. **Learn from pandas/scikit-learn** - proven patterns in the ecosystem
5. **Gather feedback early** - validate with real users before major changes

### Recommended Implementation Priority

1. ✅ **HIGH PRIORITY**: Method chaining in existing classes
2. ⭐ **MEDIUM PRIORITY**: Builder pattern for complex construction
3. 💡 **LOW PRIORITY**: Unified facade for simplified access
4. 🔮 **FUTURE**: Pipeline composition and advanced features

The fluid API improvements will make PyGrowthStandards more accessible to beginners while providing power users with the flexibility they need for complex workflows.

---

## Appendix

### References

- **pandas Documentation**: https://pandas.pydata.org/docs/
- **scikit-learn API Design**: https://scikit-learn.org/stable/developers/develop.html
- **Fluent Interfaces in Python**: https://martinfowler.com/bliki/FluentInterface.html
- **Python Builder Pattern**: https://refactoring.guru/design-patterns/builder/python/example
- **PEP 8 Style Guide**: https://peps.python.org/pep-0008/

### Feedback and Contributions

This is a living document. Please provide feedback via:
- GitHub Issues: https://github.com/Yannngn/pygrowthstandards/issues
- GitHub Discussions: https://github.com/Yannngn/pygrowthstandards/discussions
- Email: contato.yannnob@gmail.com

### Version History

- **v1.0** (Feb 2026): Initial research document
