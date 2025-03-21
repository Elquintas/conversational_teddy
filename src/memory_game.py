import os
import random
import time
import logging

from utils.audio_utils import (
    record_audio,
    play_sound,
    transcribe,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

"""
Memory game: User needs to remember a sequence of sounds.
"""


class MemoryGame:
    def __init__(self, asr_model):
        """
        Initializes the class.
        """
        self.sounds = {
            "piano": "./samples/instruments/piano.wav",
            "guitar": "./samples/instruments/guitar.wav",
            "drum": "./samples/instruments/drum.wav",
        }
        self.sequence = []
        self.asr_model = asr_model
        self.max_retries = 3
        self.audio_path = "./content/audio_robot/game/"

    def generate_sequence(self, length=3):
        """
        Generates a random sequence of sounds.
        """
        self.sequence = [random.choice(list(self.sounds.keys())) for _ in range(length)]

    def play_sequence(self):
        """
        Plays the generated sound sequence.
        """
        logger.info("Listen to the sequence:")
        for sound_id in self.sequence:
            logger.info(sound_id)
            play_sound(self.sounds[sound_id])
            time.sleep(0.5)  # Small Pause between sounds

    def get_user_input(self) -> str:
        """
        Function to record user input audio
        """
        logger.info("Say the sequence now!")
        fname = ".memory_game_audio.wav"
        record_audio(file_name=fname, audio_dur=5)
        text = transcribe(self.asr_model, fname)
        if os.path.exists(fname):
            os.remove(fname)

        return text

    def play(self) -> bool:
        """
        Main method that runs the game.
        """
        logger.info("Listen carefully to the following sequence of sounds")
        logger.info("Memorize the order, and say it correctly afterwards!")

        max_ctr = 0
        self.generate_sequence()

        while max_ctr < self.max_retries:

            self.play_sequence()
            user_sequence = self.get_user_input()
            game_sequence = " ".join(self.sequence)

            logger.info(f"Ground truth sequence : {game_sequence}")
            logger.info(f"Transcribed sequence  : {user_sequence}")

            if game_sequence == user_sequence:
                logger.info("Correct! You have a great memory!")
                play_sound("./samples/system/correct.wav")
                return True
            else:
                logger.info(f"Wrong! The correct sequence was: {game_sequence}")
                logger.info("Try again!")
                play_sound("./samples/system/wrong.wav")
                play_sound(self.audio_path + "try_again3.wav")
                max_ctr += 1

        return False
