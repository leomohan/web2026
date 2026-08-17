#!/bin/zsh
cd "$(dirname "$0")"
echo "Starting Site Manager — keep this window open. Press Ctrl+C to stop."
/opt/homebrew/opt/python@3.12/libexec/bin/python manager.py
