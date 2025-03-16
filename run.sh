#!/bin/bash

export CONFIG_PATH=$(pwd)/config/config.yaml

# Checks if content is already generated
if ! ls -d ./content/audio*/ &>/dev/null; then
    echo "[INFO] : No './content/audio*' subfolder found. Running audio creation step..."
    poetry run python ./tts-gen/robot/tts.py
else
    echo "[INFO] : './content/audio*' subfolder exists. Skipping audio creation."
fi

# Set the CONFIG_PATH environment variable to point to your config.yaml location
export CONFIG_PATH=$(pwd)/config/config.yaml

# Run the Python script
poetry run python src/main.py
