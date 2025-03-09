import logging
import numpy as np
import sounddevice as sd
from scipy.fftpack import fft, fftfreq

# from utils.audio_utils import record_audio, play_sound, transcribe

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class PitchGame:
    def __init__(self, asr_model, NUM_NOTES=3, DURATION=1.5):
        self.asr_model = asr_model
        self.SAMPLE_RATE = 44100  # CD-quality audio
        self.DURATION = DURATION  # seconds per note
        self.NUM_NOTES = NUM_NOTES  # Number of notes to play
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
        logger.info("Recording...")
        recording = sd.rec(
            int(self.SAMPLE_RATE * duration),
            samplerate=self.SAMPLE_RATE,
            channels=1,
            dtype=np.float32,
        )
        sd.wait()
        logger.info("Recording complete.")
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

    def play(self) -> bool:
        selected_notes = np.random.choice(
            list(self.NOTES.keys()), self.NUM_NOTES, replace=False
        )

        logger.info("\nListen to the notes and repeat them:\n")
        for note in selected_notes:
            logger.info(f"Playing: {note}")
            self.play_tone(self.NOTES[note], self.DURATION)

        logger.info("\nNow hum the notes in the same order...")
        total_duration = self.DURATION * self.NUM_NOTES
        audio = self.record_audio(total_duration)

        # Split the recording into parts corresponding to each note
        audio_segments = self.split_audio(audio, self.NUM_NOTES)

        logger.info("\nDetected Notes:")
        correct_count = 0

        for i, segment in enumerate(audio_segments):
            detected_freq = self.detect_frequencies(segment)
            detected_note = (
                self.get_closest_note(detected_freq) if detected_freq else "Unknown"
            )

            logger.info(
                f"  - Expected: {selected_notes[i]}, Detected: {detected_note} ({detected_freq:.2f} Hz)"
                if detected_freq
                else "No pitch detected."
            )

            if detected_note == selected_notes[i]:
                correct_count += 1

        # Final result
        if correct_count == self.NUM_NOTES:
            logger.info("\n✅ Perfect! You hummed all the notes correctly.\n")
            return True
        else:
            logger.info(
                f"\n❌ You got {correct_count}/{self.NUM_NOTES} correct. Try again!\n"
            )
            return False
