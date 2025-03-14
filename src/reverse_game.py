import logging
import random

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

"""
Reverse game: User needs to reverse the words of a given sentence.
"""


class ReverseGame:
    def __init__(self, asr_model):
        """
        Initializes the class.
        """
        self.asr_model = asr_model
        self.max_retries = 3

        self.subjects = ["cat", "dog", "friend", "bird", "robot"]
        self.verbs = ["sees", "likes", "chases", "finds", "hears"]
        self.adjectives = ["small", "big", "fast", "loud", "funny"]
        self.objects = ["ball", "car", "bird", "house", "song"]
        self.adverbs = ["quickly", "happily", "silently", "loudly", "gracefully"]

    def generate_sentence(self) -> str:
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

    def play(self) -> bool:
        """
        Main method used to launch an instance of the reverse game.
        """
        text = self.generate_sentence()
        solution = self.reverse_words(text)
        retry_ctr = 0

        logger.info(
            "You'll have to say the words of the following sentence in reverse."
        )

        while retry_ctr < self.max_retries:
            logger.info(f"sentence: {text}")
            answer = input()

            if answer == solution:
                logger.info("Perfect!")
                return True
            else:
                logger.info("Wrong... try again.")
                retry_ctr += 1

        logger.info("Try again some other time...")
        return False


# game = ReverseGame(asr_model="placeholder")
# game.play()
