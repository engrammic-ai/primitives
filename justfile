# primitives - Development Commands

# List available recipes
default:
    @just --list

# --- Setup ---

# Lock dependencies
lock:
    uv lock

# Sync dependencies
sync:
    uv sync

# Install development dependencies
install-dev:
    uv sync --all-extras

# --- Code Quality ---

# Run ruff linter
lint:
    uv run ruff check src tests

# Format code with ruff
format:
    uv run ruff format src tests
    uv run ruff check --fix src tests

# Check formatting without modifying
format-check:
    uv run ruff format --check src tests

# Run mypy type checker
typecheck:
    uv run mypy src

# Run all checks (lint + typecheck)
check: lint typecheck

# --- Testing ---

# Run all tests
test:
    uv run pytest

# Run tests with coverage report
coverage:
    uv run pytest --cov=src/primitives --cov-report=html --cov-report=term-missing

# --- Build ---

# Build package
build:
    uv build

# Build and check package
build-check:
    uv build
    uv run twine check dist/*

# Publish to PyPI (requires TWINE_USERNAME=__token__ TWINE_PASSWORD=<api-token>)
publish: build-check
    uv run twine upload dist/*

# --- Cleanup ---

# Remove cache and build artifacts
clean:
    #!/usr/bin/env bash
    set -euo pipefail
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    rm -rf htmlcov .coverage coverage.xml dist build 2>/dev/null || true
