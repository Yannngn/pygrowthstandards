# Contributing to PyGrowthStandards

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Yannngn/pygrowthstandards.git
   cd pygrowthstandards
   ```

2. **Set up the development environment:**
   ```bash
   uv venv --python 3.11
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

4. **Run tests:**
   ```bash
   pytest
   ```

## Building the Package

1. **Install build tools:**
   ```bash
   pip install build twine
   ```

2. **Build the package:**
   ```bash
   python -m build
   ```

3. **Check the build:**
   ```bash
   twine check dist/*
   ```

## Publishing to PyPI

### Test PyPI (recommended first)
```bash
twine upload --repository testpypi dist/*
```

### Production PyPI
```bash
twine upload dist/*
```

## Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update version in `src/pygrowthstandards/__init__.py`
- [ ] Update CHANGELOG.md
- [ ] Run all tests: `pytest`
- [ ] Run linting: `pre-commit run --all-files`
- [ ] Build package: `python -m build`
- [ ] Test package installation: `pip install dist/*.whl`
- [ ] Create git tag: `git tag v0.1.0`
- [ ] Push tag: `git push origin v0.1.0`
- [ ] Upload to PyPI: `twine upload dist/*`
