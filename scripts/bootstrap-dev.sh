#!/usr/bin/env bash
set -euo pipefail

echo "Setting up development environment.."

python -m pip install --upgrade pip
python -m pip install -e .[dev]
python -m pip install pre-commit

echo "Installing pre-commit hooks.."
python -m pre_commit install --install-hooks

echo "Running pre-commit on all files.."
python -m pre_commit run --all-files || true

echo "Bootstrap complete."
