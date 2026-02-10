#!/bin/bash
set -e

echo "Setting up RGS Types development environment..."

# 1. Python dependencies
if ! command -v poetry &> /dev/null; then
    echo "Error: poetry not found. Please install it first: https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "Installing Python dependencies..."
poetry install

# 2. C++ Requirements
echo "Checking for C++ compiler..."
if command -v clang++ &> /dev/null; then
    echo "  - Found clang++"
elif command -v g++ &> /dev/null; then
    echo "  - Found g++"
else
    echo "  - Warning: No C++ compiler found. C++ integration tests will fail."
fi

echo "Checking for nlohmann/json..."
if [ -f "/usr/include/nlohmann/json.hpp" ] || [ -f "/usr/local/include/nlohmann/json.hpp" ]; then
    echo "  - Found nlohmann/json"
else
    echo "  - Warning: nlohmann/json headers not found in standard paths."
    echo "    Try: sudo apt install nlohmann-json3-dev"
    echo "    Or set JSON_INCLUDE_DIR if installed elsewhere."
fi

# 3. TypeScript Requirements
echo "Checking for Node.js and TypeScript..."
if command -v node &> /dev/null; then
    echo "  - Found node: $(node --version)"
else
    echo "  - Warning: Node.js not found. TypeScript integration tests will fail."
fi

if command -v tsc &> /dev/null; then
    echo "  - Found tsc: $(tsc --version)"
else
    echo "  - Warning: tsc not found. Attempting to install locally if npm is available..."
    if command -v npm &> /dev/null; then
        echo "    Running: npm install -g typescript"
        # We try to install, but it might fail without sudo. 
        # Alternatively, we could suggest the user runs it.
        echo "    Please run: npm install -g typescript"
    else
        echo "    Error: npm not found. Cannot install TypeScript compiler."
    fi
fi

echo ""
echo "Setup complete. To run tests:"
echo "  poetry run pytest"
echo ""
echo "Note: If you have nlohmann/json in a non-standard path, use:"
echo "  export JSON_INCLUDE_DIR=/path/to/include"
echo "  poetry run pytest"
