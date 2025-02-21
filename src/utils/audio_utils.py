import random
import soundfile as sf
import sounddevice as sd
import scipy.io.wavfile as wavfile

def record_audio(
    file_name='./content/tmp_audio.wav', 
    audio_dur=4, 
    fs=44100, 
    channels=1, 
    dtype='int16'
) -> str:
    """
    Function to record audio after wake-word is activated
    """
    
    audio_data = sd.rec(
                        int(audio_dur * fs), 
                        samplerate=fs, 
                        channels=channels, 
                        dtype=dtype
                        )
    sd.wait()  # Wait until recording is finished

    wavfile.write(file_name, fs, audio_data)

    return file_name

  
def play_random_sound(option_list) -> None:
    """
    Plays a random sound from a content_data object
    """

    filename = random.choice(option_list)['file_path']
    play_sound(filename)


def play_sound(filename) -> None:
    """
    Playback function for any audio
    """
    
    data, fs = sf.read(filename, dtype='float32')  
    
    # Ignores the first 100 samples due to loud clicking sound
    sd.play(data[100:], 22050) #48000) #35000)
    status = sd.wait()
    
