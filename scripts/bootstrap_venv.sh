#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="${ROOT_DIR}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "Bootstrapping virtual environment in ${VENV_PATH}"

if [ ! -d "${VENV_PATH}" ]; then
  echo "Creating virtual environment with ${PYTHON_BIN}..."
  "${PYTHON_BIN}" -m venv "${VENV_PATH}"
else
  echo "Virtual environment already exists."
fi

PIP_BIN="${VENV_PATH}/bin/pip"

if [ ! -x "${PIP_BIN}" ]; then
  echo "Error: pip executable not found at ${PIP_BIN}" >&2
  exit 1
fi

echo "Upgrading pip (best effort)..."
if ! "${PIP_BIN}" install --upgrade pip; then
  echo "Warning: pip upgrade failed. Continuing with existing version." >&2
fi

echo "Installing project requirements..."
if ! "${PIP_BIN}" install -r "${ROOT_DIR}/requirements.txt"; then
  echo "Warning: dependency installation failed (likely due to offline environment)." >&2
  echo "Re-run this script when network access is available." >&2
  exit 1
fi

echo "Virtual environment ready. Activate with:"
echo "  source .venv/bin/activate"
