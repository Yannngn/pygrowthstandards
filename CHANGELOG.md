# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

