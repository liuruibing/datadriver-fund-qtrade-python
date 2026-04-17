#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "=========================================="
echo "   CZSC Local Version Deployment Script   "
echo "=========================================="

# 1. Environment Check
echo "[1/5] Checking Python Environment..."
PYTHON_BIN="python3.12"

if ! command -v $PYTHON_BIN &> /dev/null; then
    echo "Error: $PYTHON_BIN could not be found. Please ensure Python 3.12 is installed."
    exit 1
fi

echo "Using Python: $($PYTHON_BIN --version)"

# 2. Virtual Environment Setup (Optional but recommended)
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[2/5] Creating virtual environment ($VENV_DIR)..."
    $PYTHON_BIN -m venv $VENV_DIR
fi

echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# 3. Clean Installation of Dependencies
echo "[3/5] Handling Dependencies..."

# Uninstall conflicting versions if they exist
echo "Uninstalling existing czsc/rs_czsc (if any)..."
pip uninstall czsc rs_czsc -y || true

# Install Standard Requirements
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install --no-cache-dir -r requirements.txt
else
    echo "Warning: requirements.txt not found."
fi

# 4. Verify & Cleanup
echo "[4/5] Verifying Installation..."

pip list | grep -E "^czsc|rs_czsc|SQLAlchemy|uvicorn"

# 5. Configuration & Launch Info
echo "[5/5] Setup Complete."

echo "Important: Ensure the following environment variable is set when running the application:"
echo "export CZSC_USE_PYTHON=\"1\""
echo ""
echo "To start the server manually:"
echo "  source $VENV_DIR/bin/activate"
echo "  export CZSC_USE_PYTHON=\"1\""
echo "  python main.py"
echo ""
echo "Deployment successful!"
