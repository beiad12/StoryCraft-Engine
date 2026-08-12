#!/usr/bin/env sh

# One-shot dependency installer for macOS/Linux.
#
# Prefers `uv` (matches the project's pyproject.toml/uv.lock) and falls back
# to a plain `.venv` + `pip install -r requirements.txt` when `uv` isn't
# available, mirroring the two install paths already documented in the
# README. Also seeds config.toml from config.example.toml on first run so
# the WebUI has something to read.

set -e

CURRENT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$CURRENT_DIR"

echo "***** MoneyPrinterTurbo dependency installer *****"

_find_python() {
  for candidate in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

if command -v uv >/dev/null 2>&1; then
  echo "***** uv found, installing dependencies with 'uv sync --frozen' *****"
  uv sync --frozen
else
  PYTHON_BIN=$(_find_python) || {
    echo "***** No Python 3 interpreter found. Install Python 3.10+ (or uv: https://docs.astral.sh/uv/) and re-run this script. *****"
    exit 1
  }
  echo "***** uv not found, falling back to $PYTHON_BIN + pip *****"

  if [ ! -d "$CURRENT_DIR/.venv" ]; then
    echo "***** Creating virtual environment in .venv *****"
    "$PYTHON_BIN" -m venv .venv
  fi

  "$CURRENT_DIR/.venv/bin/python" -m pip install --upgrade pip
  "$CURRENT_DIR/.venv/bin/python" -m pip install -r requirements.txt
fi

if [ ! -f "$CURRENT_DIR/config.toml" ]; then
  echo "***** Creating config.toml from config.example.toml *****"
  cp "$CURRENT_DIR/config.example.toml" "$CURRENT_DIR/config.toml"
fi

echo "***** Install complete! Run ./webui.sh (macOS/Linux) or webui.bat (Windows) to start the WebUI. *****"

# When double-clicked from Finder, Terminal.app runs this with a tty attached
# and may close the window immediately once the script exits. Pausing here
# gives the user a chance to actually read the output above.
if [ -t 0 ]; then
  printf '\nPress Enter to close this window...'
  read -r _ || true
fi
