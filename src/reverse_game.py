import logging
import os
import random
import time

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
Reverse game: User needs to reverse the words of a given sentence.
"""


class ReverseGame:
    def __init__(self, asr_model, DIFFICULTY="easy"):
        """
        Initializes the class.
        """
        self.asr_model = asr_model
        self.max_retries = 3

        self.difficulty = DIFFICULTY

        self.audio_path = "./content/audio_robot/game/"

        self.subjects = ["cat", "dog", "friend", "bird", "robot"]
        self.verbs = ["sees", "likes", "chases", "finds", "hears"]
        self.adjectives = ["small", "big", "fast", "loud", "funny"]
        self.objects = ["ball", "car", "bird", "house", "song"]
        self.adverbs = ["quickly", "happily", "silently", "loudly", "gracefully"]

    def generate_sentence_easy(self) -> str:
        """
        Generates or gathers a random easy sentence.
        """
        return (
            f"{random.choice(self.subjects)} "
            f"{random.choice(self.verbs)} "
            f"{random.choice(self.objects)} "
        )

    def generate_sentence_medium(self) -> str:
        """
        Generates or gathers a random medium sentence.
        """
        return (
            f"{random.choice(self.subjects)} "
            f"{random.choice(self.verbs)} "
            f"{random.choice(self.adjectives)} "
            f"{random.choice(self.objects)} "
        )

    def generate_sentence_hard(self) -> str:
        """
        Generates or gathers a random sentence.
        """
        return (
            f"{random.choice(self.subjects)} "
            f"{random.choice(self.verbs)} "
            f"{random.choice(self.adjectives)} "
            f"{random.choice(self.objects)} "
            f"{random.choice(self.adverbs)}"
        )

    def reverse_words(self, sentence) -> str:
        """
        Reverses the words in that sentence.
        """
        return " ".join(sentence.split()[::-1])

    def play_sequence(self, sentence) -> str:
        """
        Plays a given random input sequence
        """
        words = sentence.split()
        for word in words:
            play_sound(self.audio_path + word + ".wav")
            time.sleep(0.35)

    def get_user_input(self) -> str:
        """
        Function to record user input audio
        """
        logger.info("Say the sequence now!")
        fname = ".reverse_game_audio.wav"
        record_audio(file_name=fname, audio_dur=5)
        text = transcribe(self.asr_model, fname)
        if os.path.exists(fname):
            os.remove(fname)
        return text

    def play(self) -> bool:
        """
        Main method used to launch an instance of the reverse game.
        """
        if self.difficulty == "easy":
            text = self.generate_sentence_easy()
        elif self.difficulty == "medium":
            text = self.generate_sentence_medium()
        else:
            text = self.generate_sentence_hard()

        logger.info(text)
        solution = self.reverse_words(text)
        retry_ctr = 0

        logger.info(
            "You'll have to say the words of the following sentence in reverse."
        )

        while retry_ctr < self.max_retries:
            logger.info(f"sentence: {text}")
            self.play_sequence(text)
            answer = self.get_user_input()

            if answer == solution:
                logger.info("Perfect!")
                play_sound("./samples/system/correct.wav")
                return True
            else:
                logger.info("Wrong... try again.")
                play_sound("./samples/system/wrong.wav")
                play_sound(self.audio_path + "try_again1.wav")
                retry_ctr += 1

        logger.info("Try again some other time...")
        return False
