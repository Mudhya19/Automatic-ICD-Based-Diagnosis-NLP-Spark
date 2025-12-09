#!/bin/bash

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi
# Start Jupyter Lab
echo "Starting Jupyter Lab..."
jupyter lab