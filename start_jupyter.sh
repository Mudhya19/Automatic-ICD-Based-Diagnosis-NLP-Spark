#!/bin/bash

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    if [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    elif [ -f ".venv\\Scripts\\activate" ]; then
        source .venv\\Scripts\\activate
    elif [ -f ".venv/bin/activate" ]; then
        echo "Unix-style virtual environment found on Windows. Recreating for Windows compatibility..."
        rm -rf .venv
        python3 -m venv .venv
        source .venv/Scripts/activate
    else
        echo "Virtual environment activation script not found for Windows"
        exit 1
    fi
else
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    elif [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    elif [ -f ".venv\\Scripts\\activate" ]; then
        source .venv\\Scripts\\activate
    else
        echo "Virtual environment activation script not found"
        exit 1
    fi
fi

# Start Jupyter Lab
echo "Starting Jupyter Lab..."
jupyter lab
