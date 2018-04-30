#!/usr/bin/env bash

GIT_DIR=$(git rev-parse --git-dir)

echo "Installing hooks \o/"

# add symlink to pre-commit script, so that we can have it in the repo
ln -s ../../hooks/pre-commit.sh $GIT_DIR/hooks/pre-commit
echo "Done 😎"

