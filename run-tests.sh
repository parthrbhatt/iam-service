#!/bin/bash

source .venv/bin/activate
python -m pytest tests/ -c tests/pytest.ini -v --tb=short --color=yes
deactivate

# Cleanup
if [ -e test.db ]; then
    rm test.db
fi
