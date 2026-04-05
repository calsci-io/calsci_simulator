#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required to initialize simulator submodules" >&2
  exit 1
fi

git -C "$REPO_DIR" submodule sync --recursive
git -C "$REPO_DIR" submodule update --init --recursive --remote
