import os
import sys
import yaml
import json
import time
import random
import logging
import numpy as np
import pyaudio as pa

from functools import partial

from utils.nemo_utils import load_nemo_models
from utils.audio_utils import (
    record_audio,
    play_random_sound,
    play_sound,
    microphone_setup,
)
from logic_manager import audio_process

# Adds the root directory of the project to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Creates shared object (dict), for exit condition
shared_state = {"exit_cond": False}

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_config(file_path: str) -> dict:
    """
    Loads parameters config file
    """
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def callback(
    in_data, frame_count, time_info, status, vad, mbn, vad_threshold
) -> tuple[bytes, int]:
    """
    Callback function for streaming audio and performing inference
    """

    signal = np.frombuffer(in_data, dtype=np.int16)
    vad_result = vad.transcribe(signal)
    mbn_result = mbn.transcribe(signal)

    stop_stream = False

    if len(vad_result):
        # if speech prob is higher than threshold, we decide it contains
        # speech utterance and activate MatchBoxNet

        if vad_result[3] >= vad_threshold:
            logger.info(f"Keyword detected: {mbn_result}")

            if mbn_result[0] == "marvin":
                stop_stream = True

            if mbn_result[0] == "stop":
                stop_stream = True
                shared_state["exit_cond"] = True

        else:
            logger.info("no speech detected")

    if stop_stream:
        return (in_data, pa.paAbort)

    return (in_data, pa.paContinue)


def main():

    CONFIG_PATH = os.getenv("CONFIG_PATH", None)
    CONFIG = load_config(CONFIG_PATH)

    # Loads content file from config
    content_file = CONFIG["content"]["content_file"]
    with open(content_file, "r") as file:
        content_data = json.load(file)

    SAMPLE_RATE = CONFIG["KWS"]["samplerate"]
    vad_threshold = CONFIG["KWS"]["vad_threshold"]
    STEP = CONFIG["KWS"]["step_size"]
    CHANNELS = CONFIG["KWS"]["channels"]
    CHUNK_SIZE = int(STEP * SAMPLE_RATE)

    # Loads pre-trained models
    vad, mbn, asr = load_nemo_models(CONFIG)

    # Function wrapper for callback function
    # Used to pass vbn and mbn models as arguments
    wrapped_callback = partial(callback, vad=vad, mbn=mbn, vad_threshold=vad_threshold)

    # Sets up microphone ID
    dev_idx = microphone_setup(CONFIG)
    p = pa.PyAudio()

    logger.info("MARVIN STARTED")
    streaming = True

    intro_file_list = content_data["intentions"]["intro"]["options"]
    play_random_sound(intro_file_list)

    while True:

        if not p == pa.PyAudio():
            p = pa.PyAudio()
        if streaming:

            # streaming
            stream = p.open(
                format=pa.paInt16,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                input_device_index=dev_idx,
                stream_callback=wrapped_callback,
                frames_per_buffer=CHUNK_SIZE,
            )

            logger.info("Listening...")
            stream.start_stream()

            # Interrupt kernel and then speak for a few more
            # words to exit the pyaudio loop !
            try:
                while stream.is_active():
                    time.sleep(0.1)
            finally:
                streaming = False
                stream.stop_stream()
                stream.close()
                p.terminate()
                logger.info("PyAudio stopped.")

        # Checks for exit condition
        if shared_state["exit_cond"]:

            # Plays random 'bye' audio file
            bye_file_list = content_data["intentions"]["bye"]["options"]
            play_random_sound(bye_file_list)

            logger.info("EXITING MARVIN.")
            sys.exit()

        time.sleep(0.5)

        # Plays random 'hello' audio file
        hello_file_list = content_data["intentions"]["hello"]["options"]
        play_random_sound(hello_file_list)

        # Records audio clip to send to server
        logger.info("Recording audio...")
        tmp_audio = record_audio(
            audio_dur=CONFIG["rec_duration"],
            fs=CONFIG["rec_samplerate"],
            channels=CONFIG["rec_channels"],
        )
        logger.info("Audio saved to {}".format(tmp_audio))

        response_file, intent = audio_process(tmp_audio, asr, content_data)

        if os.path.exists(tmp_audio):
            os.remove(tmp_audio)

        if os.path.exists(response_file):
            # plays occasionally a random prefix to intent response
            if random.random() < 0.75 and intent != "no-understand" and intent != "bye":
                time.sleep(0.3)
                prefix_file_list = content_data["intentions"]["prefix"]["options"]
                play_random_sound(prefix_file_list)

            time.sleep(0.3)
            play_sound(response_file)
        else:
            logger.warning("Audio file not found.")

        # Resets streaming flag for loop continuity
        streaming = True


if __name__ == "__main__":
    main()
