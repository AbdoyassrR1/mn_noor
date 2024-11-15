#!/bin/bash

apt update && apt install -y python3-pip

# Ensure pip is installed in the virtual environment
python3 -m ensurepip --upgrade
pip install --upgrade pip

# Install required Python dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found! Please ensure the file exists."
    exit 1
fi

# Navigate to the app directory
cd app/

# Set environment variables for Flask app
export FLASK_APP=app.py
export FLASK_ENV=development  # Change to production if needed

# Initialize the database if not already done
if [ ! -d "migrations" ]; then
    flask db init
fi

# Generate and apply migration scripts
flask db migrate
flask db upgrade
