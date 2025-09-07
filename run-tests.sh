#!/bin/bash

source venv/bin/activate
python -m pytest tests/ -v --tb=short --color=yes
