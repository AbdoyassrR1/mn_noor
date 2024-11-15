#!/bin/bash

# Initialize the database if not already done
if [ ! -d "migrations" ]; then
    flask db init
fi

# Generate and apply migration scripts
flask db migrate
flask db upgrade
