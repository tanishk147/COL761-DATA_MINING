#!/bin/bash
# env.sh - Environment setup for Part 3

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found. Please ensure python3 is installed."
    exit 1
fi

export PATH="$HOME/.local/bin:$PATH"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip

python3 -c "import numpy" 2>/dev/null || pip install numpy
python3 -c "import networkx" 2>/dev/null || pip install networkx

echo "Environment ready. Virtualenv activated."