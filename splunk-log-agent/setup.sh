#!/bin/bash

# Setup script for Splunk Log Reader Agent

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit the .env file with your Splunk credentials."
fi

echo "Setup complete!"
echo "To activate the environment, run: source venv/bin/activate"
echo "To run the command-line agent: python splunk_log_reader.py --interactive"
echo "To run the web interface: python web_interface.py"