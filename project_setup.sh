#!/bin/bash

# This script sets up a Python virtual environment and installs dependencies.

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies from requirements.txt..."
# Ensure requirements.txt exists and contains 'requests==2.32.3'
pip install -r requirements.txt

echo "Project setup complete. To activate the environment, run: source venv/bin/activate"
