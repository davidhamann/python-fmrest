#!/usr/bin/env bash

# exit as soon as any line fails
set -e

# make sure we are always in our project's root dir
cd "${0%/*}/.."

echo "running all tests..."
pytest

# exit with the exit code of the pytest call
exit $?

