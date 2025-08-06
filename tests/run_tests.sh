#!/bin/bash
# Run all tests with PYTHONPATH set to workspace root
export PYTHONPATH=.
pytest "$@"
