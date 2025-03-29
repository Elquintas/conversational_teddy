import random
import re
import logging

from game_manager import SpeechGameInterface
from utils.audio_utils import transcribe

running = True
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
)

"""
Function used to process the recorded audio file
"""


def audio_process(filename, asr_model, content_data):

    # Transcribes recorded audio file
    prompt = transcribe(asr_model, filename)

    # Applies logic to the transcription
    audio_response = teddy_server_logic(prompt, content_data, asr_model)

    return audio_response


"""
Logic function for teddy interaction based on simple regex expressions.

Teddy currently supports 6 main intentions:
 - Story
 - Joke
 - Fact
 - Riddle
 - proverb
 - tongue twister

"""


def teddy_server_logic(prompt, data, asr_model):

    option_list = data["intentions"]["no-understand"]["options"]
    ret_file = random.choice(option_list)["file_path"]

    if prompt == [""]:
        return ret_file, "no-understand"

    story_pattern = r"(story|tale)"
    joke_pattern = r"(joke|laugh)"
    fact_pattern = r"(fact|effect|affect)"
    riddle_pattern = r"(riddle|ribal|rival)"
    proverb_pattern = r"(proverb|phrase|wisdom|traditional|prover)"
    tonguetwister_pattern = r"(tongue|twister|toister|tonggue|twistter)"

    game_pattern = r"(set|free|set you free|break|curse|escape)"

    if re.search(story_pattern, prompt):
        option_list = data["intentions"]["story"]["options"]
        return random.choice(option_list)["file_path"], "story"

    elif re.search(joke_pattern, prompt):
        option_list = data["intentions"]["joke"]["options"]
        return random.choice(option_list)["file_path"], "joke"

    elif re.search(fact_pattern, prompt):
        option_list = data["intentions"]["fact"]["options"]
        return random.choice(option_list)["file_path"], "fact"

    elif re.search(riddle_pattern, prompt):
        option_list = data["intentions"]["riddle"]["options"]
        return random.choice(option_list)["file_path"], "riddle"

    elif re.search(proverb_pattern, prompt):
        option_list = data["intentions"]["proverb"]["options"]
        return random.choice(option_list)["file_path"], "proverb"

    elif re.search(tonguetwister_pattern, prompt):
        option_list = data["intentions"]["tongue-twister"]["options"]
        return random.choice(option_list)["file_path"], "tonguetwister"

    elif re.search(game_pattern, prompt):
        game_manager = SpeechGameInterface(asr_model)
        game_manager.run()

        option_list = data["intentions"]["bye"]["options"]
        return random.choice(option_list)["file_path"], "bye"

    return ret_file, "no-understand"
