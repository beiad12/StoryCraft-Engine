#!/usr/bin/env sh

# Double-click entry point for macOS Finder. Finder runs .command files in
# Terminal.app; this just delegates to install.sh so there is one script to
# maintain instead of two copies drifting apart.

CURRENT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$CURRENT_DIR/install.sh"
