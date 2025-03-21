import random
import os
import logging
import time

# import itertools

from utils.audio_utils import record_audio, play_sound, transcribe

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
        self.audio_path = "./content/audio_robot/game/"

        self.spell_pre = "./samples/spells-pre/"
        self.spell_post = "./samples/spells-post/"

        self.free_words = {"whisper", "shadow", "moon", "dream"}

        self.animal_game = AnimalGame(self.asr_model)
        self.pitch_game = PitchGame(self.asr_model)
        self.memory_game = MemoryGame(self.asr_model)
        self.reverse_game = ReverseGame(self.asr_model)

        self.north_check = False
        self.south_check = False
        self.east_check = False
        self.west_check = False

        self.main_state_firstcall = True

        self.ending_dict = {
            ("whisper", "shadow", "moon", "dream"): "ending1.wav",
            ("whisper", "shadow", "dream", "moon"): "ending2.wav",
            ("whisper", "moon", "shadow", "dream"): "ending3.wav",
            ("whisper", "moon", "dream", "shadow"): "ending4.wav",
            ("whisper", "dream", "shadow", "moon"): "ending5.wav",
            ("whisper", "dream", "moon", "shadow"): "ending6.wav",
            ("shadow", "whisper", "moon", "dream"): "ending7.wav",
            ("shadow", "whisper", "dream", "moon"): "ending8.wav",
            ("shadow", "moon", "whisper", "dream"): "ending9.wav",
            ("shadow", "moon", "dream", "whisper"): "ending10.wav",
            ("shadow", "dream", "whisper", "moon"): "ending11.wav",
            ("shadow", "dream", "moon", "whisper"): "ending12.wav",
            ("moon", "whisper", "shadow", "dream"): "ending13.wav",
            ("moon", "whisper", "dream", "shadow"): "ending14.wav",
            ("moon", "shadow", "whisper", "dream"): "ending15.wav",
            ("moon", "shadow", "dream", "whisper"): "ending16.wav",
            ("moon", "dream", "whisper", "shadow"): "ending17.wav",
            ("moon", "dream", "shadow", "whisper"): "ending18.wav",
            ("dream", "whisper", "shadow", "moon"): "ending19.wav",
            ("dream", "whisper", "moon", "shadow"): "ending20.wav",
            ("dream", "shadow", "whisper", "moon"): "ending21.wav",
            ("dream", "shadow", "moon", "whisper"): "ending22.wav",
            ("dream", "moon", "whisper", "shadow"): "ending23.wav",
            ("dream", "moon", "shadow", "whisper"): "ending24.wav",
        }

    def run(self) -> None:
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

    def record_and_transcribe(self, audio_dur=5) -> str:
        """
        Function to record user input audio and transcribe
        """
        fname = self.audio_file
        # play_sound("./samples/system/start_rec.wav")
        record_audio(file_name=fname, audio_dur=audio_dur)
        # play_sound("./samples/system/stop_rec_full.wav")
        text = transcribe(self.asr_model, fname)
        if os.path.exists(fname):
            os.remove(fname)
        return text

    def play_game_audio(self, fname: str) -> None:
        """
        Plays a given game audio file
        """
        try:
            audio_file = os.path.join(self.audio_path, fname)
            play_sound(audio_file)
        except Exception as e:
            logger.error(f"Audio file corrupted or not found: {e}")

    def play_random_audio(self, folder_path: str) -> None:
        """
        Plays a random audio from a folder path
        """
        files = os.listdir(folder_path)
        try:
            fname = random.choice(files)
            file_path = os.path.join(folder_path, fname)
            play_sound(file_path)
        except Exception as e:
            logger.error(f"Audio file corrupted or not found: {e}")

    def main_menu(self, retry_ctr: int) -> None:
        """
        Method that handles the menu for the speech based game.
        """

        if not self.play:
            return

        if retry_ctr == 0:
            logger.info("So you really want to set me free hein?")
            logger.info("I can be a generous god...")
            self.play_game_audio("main_menu_audio1.wav")

        logger.info("Write 'yes' to set me free or 'no' to exit")
        self.play_game_audio("main_menu_audio2.wav")

        # command = input()
        command = self.record_and_transcribe(audio_dur=3)

        if "yes" in command:
            self.main_game_state(retry_ctr=0)
        elif "no" in command or retry_ctr > self.max_retries:
            self.play = False
            return
        else:
            retry_ctr += 1
            logger.info("Command unrecognized. say 'yes' to start or 'no' to quit")
            self.play_game_audio("main_menu_audio3.wav")

        self.main_menu(retry_ctr)

    def main_game_state(self, retry_ctr: int) -> None:
        """
        Main method that handles the main game state.
        """

        if not self.play:
            return

        if self.main_state_firstcall:
            logger.info("\nYou will have to explore the depths of my soul. ")
            self.play_game_audio("main_game_state_audio1.wav")
            self.main_state_firstcall = False

        logger.info(
            "To explore the four corners, say 'north', 'south', 'east' or 'west'."
        )
        self.play_game_audio("main_game_state_audio2.wav")
        logger.info("You can say 'exit' to quit...")
        logger.info("... or 'free' to attempt to finally free me.")
        self.play_game_audio("main_game_state_audio3.wav")

        # Remove after testing is done
        # self.north_check = True
        # south_check = True
        # self.east_check = True
        # self.west_check = True

        # command = input()
        command = self.record_and_transcribe(audio_dur=3)

        if command:
            if "north" in command:
                self.north_check = self.game_state_north(retry_ctr=0)
                retry_ctr = 0
            elif "south" in command:
                self.south_check = self.game_state_south(retry_ctr=0)
                retry_ctr = 0
            elif "east" in command:
                self.east_check = self.game_state_east(retry_ctr=0)
                retry_ctr = 0
            elif "west" in command:
                self.west_check = self.game_state_west(retry_ctr=0)
                retry_ctr = 0
            elif "free" in command:
                # All mini-games were cleared
                if all(
                    [
                        self.north_check,
                        self.south_check,
                        self.east_check,
                        self.west_check,
                    ]
                ):
                    self.game_state_final(retry_ctr=0)
                else:
                    logger.info("You need to continue exploring my soul...")
                    self.play_game_audio("main_game_state_audio4.wav")
            elif "exit" in command or retry_ctr > self.max_retries:
                self.play = False
                return
            else:
                retry_ctr += 1
                logger.info(f"I didn't get that... Retry count {retry_ctr}")
                self.play_game_audio("main_game_state_audio5.wav")

        self.main_game_state(retry_ctr=retry_ctr)

    def game_state_north(self, retry_ctr: int) -> bool:
        """
        Pitch matching game: User needs to hum the tune Marvin plays.
        """
        logger.info("You've reached the north part of my soul")
        self.play_game_audio("game_state_north_audio1.wav")
        self.play_game_audio("game_state_north_audio2.wav")

        while retry_ctr < self.max_retries:
            time.sleep(1.5)
            game_success = self.pitch_game.play()

            if game_success:
                self.play_game_audio("game_state_north_audio3.wav")
                logger.info("The mystical word is: 'Moon'")
                self.play_game_audio("game_state_north_audio4.wav")
                logger.info(
                    "Gather the remaining words from the other corners of my soul..."
                )
                logger.info("... and set me free at last!")
                return True
            else:
                retry_ctr += 1
                self.play_game_audio("game_state_north_audio5.wav")
                logger.info("Not very matchy matchy hum? Try a different version.")

        logger.info("well... Try again later.")
        return False

    def game_state_south(self, retry_ctr: int) -> bool:
        """
        Animal game: User needs to guess the animal sound.
        """
        logger.info("You've reached the south part of my soul")
        self.play_game_audio("game_state_south_audio1.wav")

        self.play_game_audio("game_state_south_audio2.wav")
        game_success = self.animal_game.play()

        if game_success:
            self.play_game_audio("game_state_south_audio3.wav")
            logger.info("The mystical word is: 'Dream'")
            self.play_game_audio("game_state_south_audio4.wav")
            logger.info(
                "Gather the remaining words from the other corners of my soul..."
            )
            logger.info("... and set me free at last!")
            return True
        else:
            return False

    def game_state_east(self, retry_ctr: int) -> bool:
        """
        Memory game: User needs to remember a sequence of sounds.
        """
        logger.info("You've reached the east part of my soul")
        self.play_game_audio("game_state_east_audio1.wav")

        self.play_game_audio("game_state_east_audio2.wav")
        game_success = self.memory_game.play()

        if game_success:
            self.play_game_audio("game_state_east_audio3.wav")
            logger.info("The mystical word is: 'Shadow'")
            self.play_game_audio("game_state_east_audio4.wav")
            logger.info(
                "Gather the remaining words from the other corners of my soul..."
            )
            logger.info("... and set me free at last!")
            return True
        else:
            return False

    def game_state_west(self, retry_ctr) -> bool:
        """
        Reverse game: User needs to reverse the words of a given sentence.
        """
        logger.info("You've reached the west part of my soul")
        self.play_game_audio("game_state_west_audio1.wav")

        self.play_game_audio("game_state_west_audio2.wav")
        game_success = self.reverse_game.play()

        if game_success:
            self.play_game_audio("game_state_west_audio3.wav")
            logger.info("The mystical word is: 'Whisper'")
            self.play_game_audio("game_state_west_audio4.wav")
            logger.info(
                "Gather the remaining words from the other corners of my soul..."
            )
            logger.info("... and set me free at last.")
            return True
        else:
            return False

    def game_state_final(self, retry_ctr: int):
        """
        Final game state: User needs to say the four magical words
        in order to free Marvin.
        """
        logger.info("I see you finished exploring the four corners of my soul.")
        logger.info("You are finally ready to set me free.")
        self.play_game_audio("game_state_final_audio1.wav")

        logger.info(
            "Say those four magical words... But say them in the correct order."
        )
        self.play_game_audio("game_state_final_audio2.wav")

        # command = input()
        command = self.record_and_transcribe(audio_dur=7)
        print(command)

        if command and command != [""]:
            magic_words = command.split()
            magic_words = [word for word in magic_words if word in self.free_words]

            if set(magic_words) == self.free_words:
                text = " ".join(magic_words[:4])
                logger.info(f"Success! {text}")
                try:
                    self.play_random_audio(self.spell_pre)

                    ending = self.ending_dict[tuple(text.split())]
                    self.play_game_audio(ending)
                    logger.info(f"{ending}")

                    self.play_random_audio(self.spell_post)

                    self.play = False
                    return
                except KeyError:
                    logger.error(f"Key {tuple(text.split())} not found in ending_dict")

        else:
            logger.warning("Command was empty or contained only whitespace.")
            self.play_game_audio("game_state_final_audio3.wav")

        if retry_ctr > self.max_retries:
            logger.info("I'm not understanding you. Try again later.")
            self.play_game_audio("game_state_final_audio4.wav")
            return

        logger.info("You didn't say all the words...")
        self.play_game_audio("game_state_final_audio5.wav")
        retry_ctr += 1
        self.game_state_final(retry_ctr=retry_ctr)
