#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run the app with Uvicorn
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload