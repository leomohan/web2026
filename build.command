#!/bin/zsh
cd "$(dirname "$0")"
python3 build.py
echo
read "?Press Enter to close..."
