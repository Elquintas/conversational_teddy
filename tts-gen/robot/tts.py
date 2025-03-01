import os
import csv
import json
import librosa
import numpy as np
import soundfile as sf
from pedalboard.io import AudioFile
from pedalboard import Reverb, Compressor, Pedalboard
from gtts import gTTS
from pydub import AudioSegment


board = Pedalboard(
    [
        Reverb(room_size=0.50, damping=0.25, dry_level=0.75, wet_level=0.25),
        Compressor(),
    ]
)


def ring_modulator(audio_file: str, carrier_freq: int):
    """
    Function that applies a ring modulator to distort input speech
    """

    audio, sr = librosa.load(audio_file, sr=None)
    t = np.arange(len(audio)) / sr
    carrier = np.sin(2 * np.pi * carrier_freq * t)

    modulated_audio = audio * carrier
    modulated_audio = np.clip(modulated_audio, -1.0, 1.0)

    sf.write("example1.wav", modulated_audio, sr)


def voice_modification(board, output_audio_file):
    """
    Function that applies a pipeline of voice effects
    """

    audio, sr = librosa.load("example1.wav")

    # Adds a reverb tail
    audio = np.append(audio, [0.0] * 5000)

    # Shifts the pitch down
    audio = librosa.effects.pitch_shift(audio, sr=sr, n_steps=2.5)

    sf.write("temp_audio.wav", audio, sr)
    with AudioFile("temp_audio.wav") as f:

        # Open an audio file to write to:
        with AudioFile(output_audio_file, "w", f.samplerate, f.num_channels) as o:

            # Read one second of audio at a time, until the file is empty:
            while f.tell() < f.frames:
                chunk = f.read(f.samplerate)

                # Run the audio through our pedalboard:
                effected = board(chunk, f.samplerate, reset=False)

                # Write the output to our output file:
                o.write(effected)


# Function to convert text to speech
def text_to_speech(
    input_file, intent, output_directory, board, sample_rate=48000, speed_factor=1.15
):
    """
    Main function for TTS generation
    """

    os.makedirs(output_directory, exist_ok=True)

    file_list = []

    i = 1
    # Read text from the input file
    with open(input_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # content_type = row["content_type"]
            text = row["text"]

            output_audio_file = os.path.join(output_directory, f"{intent}_{i}.wav")
            i += 1

            # Generate speech from text using Google Text-to-Speech (gTTS)
            tts = gTTS(text, lang="en", tld="co.uk")
            tts.save("temp_audio.mp3")

            # Load the audio file
            audio = AudioSegment.from_mp3("temp_audio.mp3")

            audio = audio._spawn(
                audio.raw_data,
                overrides={"frame_rate": int(audio.frame_rate * speed_factor)},
            )

            audio = audio.set_frame_rate(sample_rate)

            ring_modulator("temp_audio.mp3", carrier_freq=100)

            voice_modification(board, output_audio_file)

            os.remove("temp_audio.mp3")
            os.remove("example1.wav")

            print(f"Speech saved to {output_audio_file}")

            file_dict = {"file_path": output_audio_file[4:], "description": text}

            file_list.append(file_dict)

    return file_list


def main():

    audio_fname = "audio_robot"
    output_json_file = "../../content/marvin_content_robot.json"

    intent_dict = {
        "no-understand": "no-understand_list.csv",
        "joke": "joke_list.csv",
        "riddle": "riddle_list.csv",
        "fact": "fact_list.csv",
        "proverb": "proverb_list.csv",
        "tongue-twister": "tongue-twister_list.csv",
        "prefix": "prefix_list.csv",
        "hello": "hello_list.csv",
        "bye": "bye_list.csv",
        "story": "story_list.csv",
    }

    content = {}

    for intent, input_file in intent_dict.items():
        output_dir = f"../../content/{audio_fname}/{intent}"

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        intent_files = text_to_speech(input_file, intent, output_dir, board)

        # updates the dictionary with the new list of intent files
        content[intent] = {"intent": intent, "options": intent_files}

    # constructs the full content dictionary and converts it to a json file
    full_content = {
        "name": "Teddy voice service 1.0: Robot Preset",
        "intentions": content,
    }

    with open(output_json_file, "w") as json_file:
        json.dump(full_content, json_file, indent=4)


if __name__ == "__main__":
    main()
