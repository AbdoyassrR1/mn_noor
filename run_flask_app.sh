#!/bin/bash

# Update system and install necessary packages
apt update && apt install -y python3-pip

# Install required Python packages
pip install -r requirements.txt

# Navigate to the app directory
cd app/

# Set environment variables (update these as needed)
export FLASK_APP=app.py
export FLASK_ENV=development  # Change to production for deployment

# Initialize the database (only needed if migrations folder doesn't exist)
if [ ! -d "migrations" ]; then
    flask db init
fi

# Generate and apply migration scripts
flask db migrate
flask db upgrade
