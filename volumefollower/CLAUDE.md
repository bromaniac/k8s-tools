# VolumeFollower PROJECT GUIDE

## Build & Development
- Setup environment: `uv venv .venv && source .venv/bin/activate`
- Install dependencies: `uv pip install -e ".[dev]"`
- Run application: `python -m volumefollower.main`

## Linting & Formatting
- Lint code: `ruff check .`
- Fix auto-fixable issues: `ruff check --fix .`
- Format code: `black .`

## Code Style Guidelines
- Line length: 88 characters (Black compatible)
- Python version: 3.8+
- Docstrings: Triple quotes with summary line and param/return documentation
- Import style: Standard Python with isort organization (via Ruff)
- Error handling: Use typed exceptions and proper error propagation
- Variable naming: snake_case for variables/functions, PascalCase for classes
