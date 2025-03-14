# import random
import logging

# import itertools

# import numpy as np
# import sounddevice as sd
# from scipy.fftpack import fft, fftfreq

# from utils.audio_utils import record_audio, play_sound, transcribe

from animal_game import AnimalGame
from pitch_game import PitchGame
from memory_game import MemoryGame
from reverse_game import ReverseGame

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


"""
    Main class for game interface. Controls the overal gameplay and
    storyline aspect of this functionality.
"""


class SpeechGameInterface:
    def __init__(self, asr_model):
        """
        Initializes the class
        """

        self.play = True
        self.max_retries = 3
        self.asr_model = asr_model
        self.audio_file = ".game_audio.wav"

        self.free_words = ["whisper", "shadow", "moon", "dream"]

        self.animal_game = AnimalGame(self.asr_model)
        self.pitch_game = PitchGame(self.asr_model)
        self.memory_game = MemoryGame(self.asr_model)
        self.reverse_game = ReverseGame(self.asr_model)

    def run(self):
        """
        Initializes the game
        """

        while True:
            if self.play:
                logger.info("Starting game.")
                self.main_menu(0)
            else:
                logger.info("Exiting game.")
                return

    def main_menu(self, retry_ctr):
        """
        Method that handles the menu for the speech based game.
        """

        if not self.play:
            return

        if retry_ctr == 0:
            logger.info("So you really want to set me free hein?")
            logger.info("I can be a generous god...")

        logger.info("Write 'yes' to set me free or 'no' to exit")

        command = input()
        if "yes" in command:
            self.main_game_state(retry_ctr=0)
        elif "no" in command or retry_ctr > self.max_retries:
            self.play = False
            return
        else:
            retry_ctr += 1
            logger.info("Command unrecognized. say 'yes' to start or 'no' to quit")

        self.main_menu(retry_ctr)

    def main_game_state(self, retry_ctr):
        """
        Main method that handles the main game state.
        """

        if not self.play:
            return

        if retry_ctr == 0:
            logger.info("\nYou are going to explore the depths of my soul. ")

        logger.info(
            "To explore the four corners, say 'north', 'south', 'east' or 'west'."
        )
        logger.info("You can say 'exit' to quit...\n")

        # logger.info("Or you can say 'free' to attempt to free me.")

        command = input()
        if command:
            if "north" in command:
                # is_north_valid =
                self.game_state_north(retry_ctr=0)
                retry_ctr = 0
            elif "south" in command:
                # is_south_valid =
                self.game_state_south(retry_ctr=0)
                retry_ctr = 0
            elif "east" in command:
                # is_east_valid =
                self.game_state_east(retry_ctr=0)
                retry_ctr = 0
            elif "west" in command:
                # is_west_valid =
                self.game_state_west(retry_ctr=0)
                retry_ctr = 0

            # elif "free" in command:
            # 	self.game_state_final()

            elif "exit" in command or retry_ctr > self.max_retries:
                self.play = False
                return
            else:
                retry_ctr += 1
                logger.info(f"I didn't get that... Retry count {retry_ctr}")

        self.main_game_state(retry_ctr=retry_ctr)

    def game_state_north(self, retry_ctr):
        """
        Pitch matching game: User needs to hum the tune Marvin plays.
        """
        logger.info("You've reached the north part of my soul")
        game_success = self.pitch_game.play()

        if game_success:
            logger.info("The mystical word is: 'Moon'")
            logger.info(
                "Gather the remaining words from the other corners of my soul..."
            )
            logger.info("... and set me free at last!")
            return True
        else:
            return False

    def game_state_south(self, retry_ctr):
        """
        Animal game: User needs to guess the animal sound.
        """
        logger.info("You've reached the south part of my soul")
        game_success = self.animal_game.play()

        if game_success:
            logger.info("The mystical word is: 'Dream'")
            logger.info(
                "Gather the remaining words from the other corners of my soul..."
            )
            logger.info("... and set me free at last!")
            return True
        else:
            return False

    def game_state_east(self, retry_ctr):
        """
        Memory game: User needs to remember a sequence of sounds.
        """
        logger.info("You've reached the east part of my soul")
        game_success = self.memory_game.play()

        if game_success:
            logger.info("The mystical word is: 'Shadow'")
            logger.info(
                "Gather the remaining words from the other corners of my soul..."
            )
            logger.info("... and set me free at last!")
            return True
        else:
            return False

    def game_state_west(self, retry_ctr):
        """
        Reverse game: User needs to reverse the words of a given sentence.
        """
        logger.info("You've reached the west part of my soul")
        game_success = self.reverse_game.play()

        if game_success:
            logger.info("The mystical word is: 'Whisper'")
            logger.info(
                "Gather the remaining words from the other corners of my soul..."
            )
            logger.info("... and set me free at last.")
            return True
        else:
            return False
