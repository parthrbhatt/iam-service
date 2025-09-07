#!/bin/bash

# Create virtual environment if one doesn't exist
if [ ! -e .venv ]; then
   echo "Creating virtual environment..."
   python3 -mvenv .venv
   source .venv/bin/activate
   echo "Installing dependencies..."
   pip install -r requirements.txt
   deactivate
fi

# Create sample keys if they don't exist
if [ ! -e keys ]; then
    echo "Creating keys..."
    mkdir -p keys/sample
    openssl genrsa -out keys/sample/private.pem 2048
    openssl rsa -in keys/sample/private.pem -pubout -out keys/sample/public.pem
fi

source .venv/bin/activate
python -m pytest tests/ -c tests/pytest.ini -v --tb=short --color=yes
deactivate

# Cleanup
if [ -e test.db ]; then
    rm test.db
fi
