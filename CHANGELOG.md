# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


# [0.2.0](https://github.com/Yannngn/pygrowthstandards/compare/v0.1.3...v0.2.0) (2026-02-09)


### Features

* fluid interface for patient ([cdbd2dd](https://github.com/Yannngn/pygrowthstandards/commit/cdbd2dd3858404f1c006540eb2552e9216658cde))

## [0.1.3] - 2025-12-02

### Notes
- Published from a branch that was not merged into `main` at the time; this release is superseded by the next `main`-based release (v0.1.4+).

### Changed
- Simplified imports

### Fixed
- Fixed image link for stature growth chart

## [0.1.2] - 2025-08-22

### Added
- Initial public release
- WHO Child Growth Standards support (0-5 years)
- WHO Growth Reference Data support (5-19 years)
- INTERGROWTH-21st Project standards support
- Functional API for single calculations
- Object-oriented API for patient tracking
- Growth chart plotting capabilities
- Z-score and percentile calculations
- Support for stature, weight, BMI, and head circumference measurements
- LMS method implementation with interpolation
- Comprehensive test suite
- Configuration-based validation system

### Features
- **Dual API Design**: Both functional and object-oriented interfaces
- **Multiple Growth Standards**: WHO and INTERGROWTH-21st support
- **Age Group Handling**: Automatic age group detection and validation
- **Measurement Aliases**: Flexible input with common abbreviations (e.g., "wfa" → "weight")
- **Data Visualization**: Matplotlib-based growth chart generation
- **Performance Optimized**: Parquet-based data storage and NumPy operations

## [0.1.1] - 2025-08-22

### Changed
- Trying to publish on PyPI

### Fixed
- Fixed version for publication on TestPyPI

## [0.1.0] - 2025-08-22

### Added
- Tagged initial release

## [0.1.0b] - 2025-08-22

### Changed
- Tagged beta release (no code changes since previous tag)

## [0.1.0a1] - 2025-08-22

### Added
- Tagged alpha release (no code changes since previous tag)
