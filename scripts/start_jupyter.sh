#!/bin/bash

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    if [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    elif [ -f ".venv\\Scripts\\activate" ]; then
        source .venv\\Scripts\\activate
    else
        echo "Virtual environment activation script not found for Windows"
        exit 1
    fi
else
    source .venv/bin/activate
fi

# Start Jupyter Lab
echo "Starting Jupyter Lab..."
jupyter lab
