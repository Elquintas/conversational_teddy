import sys
import random
import logging
import pyaudio as pa
import soundfile as sf
import sounddevice as sd
import scipy.io.wavfile as wavfile

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def transcribe(asr_model, filename):
    """
    Transcribes speech given an ASR engine
    """

    logger.info("Beginning transcription...")
    transcript = asr_model.transcribe([filename])
    text = transcript[0][0]

    if text:
        logger.info("Transcribed audio - {}".format([text]))
    else:
        logger.warning("Error while transcribing.")
        text = [""]

    return text


def microphone_setup(CONFIG) -> int:
    """
    Sets up the microphone idx to be used by Marvin
    """

    p = pa.PyAudio()
    input_devices = []
    dev_idx = None

    logger.info("Available audio input devices: ")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev.get("maxInputChannels"):
            input_devices.append(i)
            logger.info(f"{i},{dev.get('name')}")

            if dev.get("name") == CONFIG["microphone_name"]:
                dev_idx = i
            elif dev.get("name") in ["sysdefault", "default"]:
                dev_idx = i

    if not input_devices:
        logger.error("No input devices found!")
        sys.exit(1)

    if dev_idx is None:
        logger.error(
            "No suitable microphone found as sysdefault. "
            "Please check your device settings."
        )
        sys.exit(1)

    logger.info("Microphone successfully configured.")

    return dev_idx


def record_audio(
    file_name="./content/tmp_audio.wav",
    audio_dur=4,
    fs=44100,
    channels=1,
    dtype="int16",
) -> str:
    """
    Function to record audio after wake-word is activated
    """

    audio_data = sd.rec(
        int(audio_dur * fs), samplerate=fs, channels=channels, dtype=dtype
    )
    sd.wait()  # Wait until recording is finished

    wavfile.write(file_name, fs, audio_data)

    return file_name


def play_random_sound(option_list) -> None:
    """
    Plays a random sound from a content_data object
    """

    filename = random.choice(option_list)["file_path"]
    play_sound(filename)


def play_sound(filename) -> None:
    """
    Playback function for any audio
    """

    data, fs = sf.read(filename, dtype="float32")

    # Ignores the first 100 samples due to loud clicking sound
    sd.play(data[100:], 22050)  # 48000) #35000)
    # status = sd.wait()
    sd.wait()
