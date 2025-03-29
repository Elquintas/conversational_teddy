# Marvin the Demon, an interactive speech-based game

## Summary

Welcome to Marvin, a demon trapped inside a voodo doll that you need to set free through simple and deterministic speech-based interactions.

Marvin currently supports the following 6 intentions:
```sh
- story
- joke
- fact
- proverb
- riddle
- tongue-twister

- I want to set you free! (speech-based game)
```

Should you attempt to free Marvin from his curse (saying: "I want to set you free!"), the system will guide you through a series of 4 minigames that award each one of the four magical words, used to release Marvin.
Once everything is complete and you've gathered all the words, you may attempt say them sequentially to set him free. But be warned! Speaking them in the different orders may trigger unforeseen consequences, leading to different endings.

## Installation

Marvin uses python 3.10.12 and poetry as a dependency manager. If you do not have poetry installed in your system, please refer to poetry's installation guide. In order to properly build the virtual environment, run the following commands (skip if already installed):

```sh
pyenv install 3.10.12
brew install portaudio ffmpeg
pipx install poetry
```
Run the following command to install the dependencies of this project

```sh
poetry install --no-root
```

Marvin relies on pre-synthesized audio files, that are retrieved following the user query. This speeds up inference, meaning that all content is already pre-generated and deterministic prior to any interactions. In order to generate the user content, please run the following script:

```sh
cd tts-gen/robot/ && poetry run python tts.py
```
This script uses a text-to-speech custom recipe to generate a robotic voice. This can take several minutes. Once the script finishes, and all content is properly generated, Marvin is ready to be launched. You only have to generate the text-to-speech audio once.

## How to Use

Export the path to the config file:

```sh
export CONFIG_PATH=$(pwd)/config/config.yaml
```

Please refer to the following command to launch a terminal-based instance of Marvin:

```sh
poetry run python src/main.py
```

Alternatively, you can run the run.sh. Note that this bash script also launches the synthatic data generation script if no generated audio is detected.

```
bash run.sh
```

Once the system properly loads, we are finally ready to interact with Marvin. Say 'Marvin' to wake the system up and ask him to tell you any one of the supported intentions for a brief interaction.

e.g.
```sh
   - you: "Marvin"
   - Marvin: "Yes?"
   - You: "Tell me a joke."
   - Marvin: "Fine... Why was the math book so sad? It had too many problems."
```

Furthermore, you can tell Marvin that you want to set him free in order to start a brief game with many possible endings.

e.g.
```sh
   - you: "Marvin"
   - Marvin: "What now?"
   - You: "I want to set you free."
   - Marvin: "So you want to set me free hein? <game class starts>."
```

## Minigames

Marvin contains 4 speech-based minigames that are prompted when someone attempts to free him. These games can have different difficulty levels based on user preference. The games are as follows:

- Pitch-based game (North Section): In this game the user needs to match the pitch of a short series of musical notes
- Animal guessing game (South Section): In this game the user needs to guess the animal sound that was played
- Memory game (East Section): The user needs to say the sequence in whicha set of three different sounds were played (piano, drum and guitar)
- Reverse game (West Section): The user needs to flip the words in a sentence (e.g. "cat sees bird" --> "bird sees cat")

The following table illustrates the difficulty levels for each game:

| Game       | easy   | medium | hard   |
|------------|--------|--------|--------|
|pitch game  |2 notes |3 notes |5 notes |
|animal game |1 sound                   |
|memory game |2 sounds|3 sounds|5 sounds|
|reverse game|3 words |4 words |5 words |

## Microphone Setup

Marvin requires a microphone to function, whose ID can vary depending on device. Currently, the system is configured to default to one of the following device names: "sysdefault" or "default", which are common in unix based system. Nevertheless, a custom microphone name can be added on the config file (./config/config.yaml). Please refer to the microphone name variable in this config (defaulted to a Macbook Pro Microphone device name) and change it accordingly.

The following simple script can be used to list all of the available devices and their corresponding names.

```sh
poetry run python extras/mic_idx_finder.py
```

## Notes

Marvin relies on a generic pre-trained keyword spotter and speech recognizer. Therefore, Marvin's transcriptions and occasional false activations are a consequence of this aspect. Over-articulation can improve his understanding.

Marvin also relies on simple regular expressions (regex) for intent classification.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## References

https://github.com/NVIDIA/NeMo/blob/main/tutorials/asr/Online_Offline_Speech_Commands_Demo.ipynb
