# PyGrowthStandards AI Coding Instructions

## Project Overview
PyGrowthStandards is a Python library for calculating child growth z-scores and percentiles using WHO and INTERGROWTH-21st standards. It provides both object-oriented and functional APIs for anthropometric calculations and visualization.

## Architecture & Data Flow

### Core Components
- **`src/data/`**: ETL pipeline (extract → transform → load) for growth reference data
- **`src/functional/`**: Stateless API for direct z-score/percentile calculations  
- **`src/oop/`**: Object-oriented API for patient tracking and visualization
- **`src/utils/`**: Configuration, statistical functions, and plotting utilities

### Data Processing Pipeline
1. **Extract** (`src/data/extract.py`): Parses WHO/INTERGROWTH Excel/CSV files into `RawTable` objects
2. **Transform** (`src/data/transform.py`): Converts age units to days, derives missing LMS parameters
3. **Load** (`src/data/load.py`): Creates `GrowthTable` objects with LMS arrays for calculations

### LMS Method Core
All calculations use the LMS (Lambda-Mu-Sigma) method:
- **L**: Box-Cox transformation parameter  
- **M**: Median value
- **S**: Coefficient of variation
- Formula: `z = (pow(value/M, L) - 1) / (L * S)` when L≠0

## Configuration System

### Type System (`src/utils/config.py`)
Use the centralized config system instead of magic strings:
```python
from src.utils.config import MeasurementTypeType, DataSexType, AgeGroupType
from src.utils.config import AGE_GROUP_CONFIG, MEASUREMENT_CONFIG
```

### Age Group Resolution
```python
# Get age limits and x_var_type from config
config = AGE_GROUP_CONFIG["0-2"]
limits = config.limits  # (0, 730)
x_type = config.x_type  # "age"
```

### Measurement Aliases
```python
# Resolve measurement aliases automatically
resolved = ChoiceValidator.resolve_measurement_alias("wfa")  # → "weight"
```

## Development Workflows

### Running the Application
```bash
# Object-oriented example
python main.py

# Functional API example  
python -c "from src import functional as F; print(F.zscore('weight', 5, 'F', age_days=30))"
```

### Testing
```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/functional/
pytest tests/oop/
```

### Data Processing
```bash
# Regenerate reference data (requires raw data files)
python -m src.data.main
```

## Key Patterns

### Dual API Design
- **Functional**: `F.zscore(measurement, value, sex, age_days)` for single calculations
- **OOP**: `Patient` + `MeasurementGroup` + `Calculator` for longitudinal tracking

### Age Handling
- All internal calculations use **days** as the standard unit
- Age groups determine which reference table to use
- Gestational age (weeks) vs postnatal age (days) requires different table selection

### Error Handling
```python
from src.utils.errors import NoReferenceDataError, InvalidChoicesError
# Custom exceptions for missing data and invalid parameters
```

### Data Validation
- Use `ChoiceValidator` methods for input validation
- All measurement types have aliases (e.g., "wfa" → "weight")
- Sex values: "M", "F", "U" (unknown)

## File Organization Conventions

### Import Patterns
- Use absolute imports: `from src.utils.config import ...`
- Avoid `sys.path` manipulation
- Run modules with: `python -m src.module.name`

### Configuration Over Code
- All choices defined in `src/utils/config.py` with validation
- Use `@dataclass(frozen=True)` for configuration objects
- Enum-based type definitions with Literal type hints

### Testing Structure
- Fixtures in `tests/oop/test_calculator.py` create sample patients
- Functional tests validate statistical accuracy
- Use `pytest` with absolute paths in `pythonpath`

## Performance Notes
- Reference data loaded once into memory (`DATA` global)
- LMS interpolation for missing age points
- Parquet format for efficient data storage
- Consider caching for frequently accessed LMS values

## Common Gotchas
- Age groups have specific measurement type restrictions (e.g., no BMI at birth)
- Length and Height were collapsed into Stature.
- Velocity measurements require interval-based age calculations
- Missing LMS values are derived from standard deviation tables using curve fitting
