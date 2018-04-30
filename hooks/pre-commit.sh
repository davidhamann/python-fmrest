#!/usr/bin/env bash

echo "Running pre-commit hook..."
./hooks/run-tests.sh

# if tests didn't exit with 0
if [ $? -ne 0 ]; then
    echo "Tests failed, commit aborted. 🤕"
    exit 1
fi
