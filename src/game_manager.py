# from utils.audio_utils import record_audio


class SpeechGameInterface:
    def __init__(self):
        self.play = True
        self.max_retries = 3

    def run(self):
        """Initializes the game"""

        while True:
            if self.play:
                self.main_menu(0)
            else:
                print("Exiting game.")
                return

    def main_menu(self, retry_ctr):
        """Main menu for the speech based game."""

        if not self.play:
            return

        print("Write 'yes' to set me free or 'no' to exit")

        command = input()
        if "yes" in command:
            self.main_game_state(0)
        elif "no" in command or retry_ctr > self.max_retries:
            self.play = False
            return
        else:
            retry_ctr += 1
            print("Command unrecognized. say 'yes' to start or 'no' to quit")

        self.main_menu(retry_ctr)

    def main_game_state(self, retry_ctr):
        """Handles the main game state."""

        if not self.play:
            return

        print("\nYou are going to explore the depths of my soul. ")
        print("To explore the four corners, say 'north', 'south', 'east' or 'west'.")
        print("You can also say 'exit' to quit...\n")

        command = input()
        if command:
            if "north" in command:
                self.game_state_north(0)
                retry_ctr = 0
            elif "south" in command:
                self.game_state_south(0)
                retry_ctr = 0
            elif "east" in command:
                self.game_state_east(0)
                retry_ctr = 0
            elif "west" in command:
                self.game_state_west(0)
                retry_ctr = 0

            elif "exit" in command or retry_ctr > self.max_retries:
                self.play = False
                return
            else:
                retry_ctr += 1
                print(f"I didn't get that... Retry count {retry_ctr}")

        self.main_game_state(retry_ctr)

    def game_state_north(self, retry_ctr):
        """
        TODO:
            Pitch matching game. Marvin plays a tone and the user has to
            match it by humming for 10 seconds.
        """
        print("You've reached the north part of my soul")

    def game_state_south(self, retry_ctr):
        print("You've reached the south part of my soul")

    def game_state_east(self, retry_ctr):
        print("You've reached the east part of my soul")

    def game_state_west(self, retry_ctr):
        print("You've reached the west part of my soul")
