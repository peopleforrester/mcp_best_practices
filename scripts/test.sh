#!/usr/bin/env bash
# ABOUTME: The light gate run on every branch: prose lint, then lint, types, and tests for every package.
# ABOUTME: Mirrors the CI prose, python, typescript, and lockdrift jobs; needs only uv and Node (corepack).
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"

for tool in uv corepack; do
  if ! command -v "$tool" >/dev/null; then
    echo "error: $tool is not on PATH; scripts/test.sh needs uv and Node's corepack" >&2
    exit 1
  fi
done

echo "== prose: em-dash check =="
if grep -rnP '\x{2014}' --include='*.md' --include='*.html' \
     --exclude='mcp-sme-portfolio-research-*.md' \
     --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=site --exclude-dir=.git \
     .; then
  echo "error: em-dash (U+2014) found in authored docs (see above)" >&2
  exit 1
fi

for d in $(find . -name pyproject.toml -not -path '*/.venv/*' -not -path '*/node_modules/*' -exec dirname {} \; | sort); do
  echo "== python: $d =="
  (
    cd "$d"
    uv run ruff check .
    if [ -d src ]; then uv run mypy --config-file "$root/mypy.ini" src; fi
    if ! find . -name 'test_*.py' -not -path '*/.venv/*' | grep -q .; then
      echo "error: $d has Python sources but no tests" >&2
      exit 1
    fi
    uv run pytest -q
  )
done

export COREPACK_ENABLE_DOWNLOAD_PROMPT=0
for d in $(find . -name package.json -not -path '*/node_modules/*' -exec dirname {} \; | sort); do
  echo "== typescript: $d =="
  ( cd "$d" && corepack pnpm install --frozen-lockfile && corepack pnpm test && corepack pnpm typecheck )
done

echo "== lockdrift: fastmcp and mcp resolve to one version across uv.lock files =="
locks=$(find . -name uv.lock -not -path '*/.venv/*')
for pkg in fastmcp mcp; do
  versions=$(grep -hA1 "^name = \"$pkg\"\$" $locks | grep '^version = ' | awk '{print $3}' | sort -u)
  echo "$pkg: ${versions:-(absent)}"
  if [ "$(echo "$versions" | grep -c .)" -gt 1 ]; then
    echo "error: $pkg resolves to multiple versions across the lockfiles" >&2
    exit 1
  fi
done

echo "all checks passed"
