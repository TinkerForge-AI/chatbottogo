#!/bin/bash
# Unified test runner: activate venv, set PYTHONPATH, run all tests from workspace root
set -e
cd "$(dirname "$0")"
if [ -d "backend/venv" ]; then
  source backend/venv/bin/activate
fi
export PYTHONPATH=.
python -m pytest "$@"
