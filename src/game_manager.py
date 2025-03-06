import random
import logging
import numpy as np
import sounddevice as sd
from scipy.fftpack import fft, fftfreq
from utils.audio_utils import record_audio, play_sound, transcribe


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AnimalGame:
    def __init__(self, asr_model):
        self.asr_model = asr_model
        self.audio_file = ".game_audio.wav"
        self.animal_lib = {
            "cow": "./samples/animals/cow.wav",
            "cricket": "./samples/animals/cricket.wav",
            "dog": "./samples/animals/dog.wav",
            "donkey": "./samples/animals/donkey.wav",
            "horse": "./samples/animals/horse.wav",
            "monkey": "./samples/animals/monkey.wav",
            "wolf": "./samples/animals/wolf.wav",
        }

    def play(self):

        logger.info("What is this sound?")

        animal = random.choice(list(self.animal_lib.keys()))
        logger.info(f"Animal to guess: {self.animal_lib[animal]}")
        play_sound(self.animal_lib[animal])

        logger.info("Guess the sound now!")
        record_audio(file_name=self.audio_file)
        text = transcribe(self.asr_model, self.audio_file)

        if animal in text:
            logger.info("success! you've guessed it.")
        else:
            logger.info("You failed... Try again next time.")


class PitchGame:
    def __init__(self, asr_model):
        self.asr_model = asr_model
        self.SAMPLE_RATE = 44100  # CD-quality audio
        self.DURATION = 1.5  # seconds per note
        self.NUM_NOTES = 3  # Number of notes to play
        self.NOTES = {
            "C3": 130.81,
            "D3": 146.83,
            "E3": 164.81,
            "F3": 174.61,
            "G3": 196.00,
            "A3": 220.00,
            "B3": 246.94,
            "C4": 261.63,
        }

    def generate_wave(
        self, frequency, duration, sample_rate=44100, wave_type="triangle"
    ):
        """Generate a waveform (sine, square, triangle, sawtooth) for a given frequency and duration."""
        t = np.linspace(0, duration, int(sample_rate * duration), False)

        if wave_type == "sine":
            wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # Smooth
        elif wave_type == "square":
            wave = 0.5 * np.sign(np.sin(2 * np.pi * frequency * t))  # Harsh, electronic
        elif wave_type == "triangle":
            wave = 0.5 * (
                2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
            )  # Flute-like
        elif wave_type == "sawtooth":
            wave = 0.5 * (2 * (t * frequency - np.floor(t * frequency)))  # String-like

        return wave.astype(np.float32)

    def play_tone(self, frequency, duration):
        """Play a sine wave of a given frequency."""
        tone = self.generate_wave(frequency, duration)
        sd.play(tone, samplerate=self.SAMPLE_RATE)
        sd.wait()

    def detect_frequencies(self, audio, sample_rate=44100):
        """Use FFT to detect the most prominent frequency in the audio."""
        N = len(audio)
        fft_result = np.abs(fft(audio))[
            : N // 2
        ]  # Compute FFT and take only positive frequencies
        frequencies = fftfreq(N, 1 / sample_rate)[: N // 2]

        # Filter only frequencies within the musical range (50 Hz to 1000 Hz)
        valid_indices = (frequencies > 50) & (frequencies < 1000)
        fft_result = fft_result[valid_indices]
        frequencies = frequencies[valid_indices]

        if len(frequencies) == 0:
            return None  # No valid frequencies detected

        # Find the most dominant frequency
        peak_index = np.argmax(fft_result)
        detected_freq = frequencies[peak_index]

        return detected_freq

    def record_audio(self, duration):
        """Record audio from the microphone."""
        print("Recording...")
        recording = sd.rec(
            int(self.SAMPLE_RATE * duration),
            samplerate=self.SAMPLE_RATE,
            channels=1,
            dtype=np.float32,
        )
        sd.wait()
        print("Recording complete.")
        return recording.flatten()

    def get_closest_note(self, freq):
        """Find the closest musical note for a given frequency."""
        return min(self.NOTES, key=lambda note: abs(self.NOTES[note] - freq))

    def split_audio(self, audio, num_segments):
        """Split the recorded audio into separate segments for each note."""
        segment_length = len(audio) // num_segments
        return [
            audio[i * segment_length : (i + 1) * segment_length]
            for i in range(num_segments)
        ]

    def play(self):
        selected_notes = np.random.choice(
            list(self.NOTES.keys()), self.NUM_NOTES, replace=False
        )

        print("\nListen to the notes and repeat them:\n")
        for note in selected_notes:
            print(f"Playing: {note}")
            self.play_tone(self.NOTES[note], self.DURATION)

        print("\nNow hum the notes in the same order...")
        total_duration = self.DURATION * self.NUM_NOTES
        audio = self.record_audio(total_duration)

        # Split the recording into parts corresponding to each note
        audio_segments = self.split_audio(audio, self.NUM_NOTES)

        print("\nDetected Notes:")
        correct_count = 0

        for i, segment in enumerate(audio_segments):
            detected_freq = self.detect_frequencies(segment)
            detected_note = (
                self.get_closest_note(detected_freq) if detected_freq else "Unknown"
            )

            print(
                f"  - Expected: {selected_notes[i]}, Detected: {detected_note} ({detected_freq:.2f} Hz)"
                if detected_freq
                else "No pitch detected."
            )

            if detected_note == selected_notes[i]:
                correct_count += 1

        # Final result
        if correct_count == self.NUM_NOTES:
            print("\n✅ Perfect! You hummed all the notes correctly.\n")
        else:
            print(
                f"\n❌ You got {correct_count}/{self.NUM_NOTES} correct. Try again!\n"
            )


class SpeechGameInterface:
    def __init__(self, asr_model):
        self.play = True
        self.max_retries = 3
        self.asr_model = asr_model
        self.audio_file = ".game_audio.wav"

        self.animal_game = AnimalGame(self.asr_model)
        self.pitch_game = PitchGame(self.asr_model)

    def run(self):
        """Initializes the game"""

        while True:
            if self.play:
                logger.info("Starting game.")
                self.main_menu(0)
            else:
                logger.info("Exiting game.")
                return

    def main_menu(self, retry_ctr):
        """Main menu for the speech based game."""

        if not self.play:
            return

        logger.info("Write 'yes' to set me free or 'no' to exit")

        command = input()
        if "yes" in command:
            self.main_game_state(0)
        elif "no" in command or retry_ctr > self.max_retries:
            self.play = False
            return
        else:
            retry_ctr += 1
            logger.info("Command unrecognized. say 'yes' to start or 'no' to quit")

        self.main_menu(retry_ctr)

    def main_game_state(self, retry_ctr):
        """Handles the main game state."""

        if not self.play:
            return

        logger.info("\nYou are going to explore the depths of my soul. ")
        logger.info(
            "To explore the four corners, say 'north', 'south', 'east' or 'west'."
        )
        logger.info("You can also say 'exit' to quit...\n")

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
                logger.info(f"I didn't get that... Retry count {retry_ctr}")

        self.main_game_state(retry_ctr)

    def game_state_north(self, retry_ctr):
        """
        TODO:
            Pitch matching game. Marvin plays a tone and the user has to
            match it by humming for 10 seconds.
        """
        logger.info("You've reached the north part of my soul")
        self.pitch_game.play()

    def game_state_south(self, retry_ctr):
        """
        TODO:
            guess the animal sound
        """
        logger.info("You've reached the south part of my soul")
        self.animal_game.play()

    def game_state_east(self, retry_ctr):
        logger.info("You've reached the east part of my soul")

    def game_state_west(self, retry_ctr):
        logger.info("You've reached the west part of my soul")
