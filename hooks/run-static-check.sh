#!/usr/bin/env bash

# exit as soon as any line fails
set -e

# make sure we are always in our project's root dir
cd "${0%/*}/.."

echo "running mypy type checks..."
mypy fmrest --ignore-missing-imports

exit $?

