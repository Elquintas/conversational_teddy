#!/bin/bash

# Set the CONFIG_PATH environment variable to point to your config.yaml location
export CONFIG_PATH=$(pwd)/config/config.yaml

# Run the Python script
poetry run python src/main.py
