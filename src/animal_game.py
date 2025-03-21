import random
import logging

from utils.audio_utils import record_audio, play_sound, transcribe

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

"""
Animal game: User needs to guess the animal sound.
"""


class AnimalGame:
    def __init__(self, asr_model):
        """
        Initializes the class.
        """
        self.asr_model = asr_model
        self.max_retries = 3
        self.audio_file = ".game_audio.wav"
        self.animal_lib = {
            "cow": "./samples/animals/cow.wav",
            "cricket": "./samples/animals/cricket.wav",
            "dog": "./samples/animals/dog.wav",
            "donkey": "./samples/animals/donkey.wav",
            "horse": "./samples/animals/horse.wav",
            # "monkey": "./samples/animals/monkey.wav",
            "wolf": "./samples/animals/wolf.wav",
            "bear": "./samples/animals/bear.wav",
            "eagle": "./samples/animals/eagle.wav",
            "raccoon": "./samples/animals/raccoon.wav",
            "pig": "./samples/animals/pig.wav",
            "monkey": "./samples/animals/monkey2.wav",
        }

    def play(self) -> bool:
        """
        Main method that runs the gameplay of the Animal Game.
        """
        retry_ctr = 0

        logger.info("What is this sound?")
        animal = random.choice(list(self.animal_lib.keys()))

        while retry_ctr <= self.max_retries:

            logger.info(f"Animal to guess: {self.animal_lib[animal]}")
            play_sound(self.animal_lib[animal])
            logger.info("Guess the sound now!")
            record_audio(file_name=self.audio_file)
            text = transcribe(self.asr_model, self.audio_file)

            if animal in text:
                logger.info("success! you've guessed it.")
                play_sound("./samples/system/correct.wav")
                return True
            else:
                logger.info("You failed... Try again")
                play_sound("./samples/system/wrong.wav")
                retry_ctr += 1

        logger.info("Well... It seems you'll have to try again some other time.")
        return False
