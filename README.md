# Marvin, an interactive storytelling bot!

## Summary

Welcome to Marvin, an interactive storytelling bot designed for very simple and deterministic speech-based  interactions.

Marvin currently supports the following 6 intentions:
```sh
    - story
    - joke
    - fact
    - proverb
    - riddle
    - tongue-twister
```

## Installation

Marvin uses poetry as a dependency manager. If you do not have poetry installed in your system, please refer to petry's installation guide.
In order to properly build the virtual environment, run the following command:

```sh
$ poetry install --no-root
```
## How to Use

Marvin relies on pre-synthesized audio files, that are retrieved following the user query. This speeds up inference, meaning that all content is already pre-generated à priori to any interactions.

In order to generate the user content, please run the following script:

```sh
poetry run python ./gen-content/robot/tts.py
```
Once the script finishes, and all content is properly generated, Marvin is ready to be launched.

Following the installation and content creation, we are finally ready to launch Marvin. Please refer to the following command to launch a terminal-based instance of the storytelling bot:

```sh
poetry run python src/tts.py
```
Once the system properly loads, we are finally ready for some interactions.

Say 'Marvin' to wake the system up and ask him to tell you any one of the 6 supported intentions for a brief interaction.

e.g.
    you: "Marvin"
    Marvin: "Yes?"
    You: "Tell me a joke."
    Marvin: "Fine... Why did the math book killed itself? It had many problems."

## Microphone Setup

Marvin requires a microphone to function, whose ID can vary depending on device. Currently, the system is configured to default to one of the following device names: "sysdefault" or "default", which are common in unix based system. Nevertheless, a custom microphone name can be added on the config file (./config/config.yaml). Please refer to the microphone name variable in this config (defaulted to a Macbook Pro Microphone device name) and change it accordingly.

The following simple script can be used to list all of the available devices and their corresponding names.

```sh
poetry run python extras/mic_idx_finder.py
```
