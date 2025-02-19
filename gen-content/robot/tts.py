import os
import csv
import uuid
import librosa
import numpy as np
import soundfile as sf
from pedalboard.io import AudioFile
from pedalboard import *
from gtts import gTTS
from pydub import AudioSegment


board = Pedalboard([
    Reverb(room_size=0.50, damping=0.25, dry_level=0.75, wet_level=0.25),
    Compressor(),
])

def ring_modulator(
        audio_file,
        carrier_freq
):
    """ Function that applies a ring modulator to distort input speech"""
    
    audio, sr = librosa.load(audio_file, sr=None)

    # Generate a carrier signal (sine wave) at a specific frequency
    #carrier_freq = 100  # Carrier frequency in Hz (adjust for effect)
    t = np.arange(len(audio)) / sr  # Time vector for the length of the audio

    # Create the carrier sine wave
    carrier = np.sin(2 * np.pi * carrier_freq * t)

    # Apply the ring modulation (multiplying the audio by the carrier signal)
    modulated_audio = audio * carrier

    # Clip the audio to ensure it is within the valid range for WAV files (-1 to 1)
    modulated_audio = np.clip(modulated_audio, -1.0, 1.0)

    # Save the modulated audio to a new file
    sf.write('example1.wav', modulated_audio, sr)

def voice_modification(
              board,
              output_audio_file
):
    """Function that applies a pipeline of voice effects"""
    
    audio, sr = librosa.load("example1.wav")

    # ADDS A ONE AND A HALF ECOND TAIL FOR REVERB TO BREATH
    audio = np.append(audio, [0.0]*5000)  

    # SHIFTES THE PITCH DOWN
    audio = librosa.effects.pitch_shift(audio, sr=sr, n_steps=2.5)

    sf.write("temp_audio.wav", audio, sr)
    with AudioFile('temp_audio.wav') as f:
        
        # Open an audio file to write to:
        with AudioFile(output_audio_file, 'w', f.samplerate, f.num_channels) as o:
  
            # Read one second of audio at a time, until the file is empty:
            while f.tell() < f.frames:
                chunk = f.read(f.samplerate)
      
                # Run the audio through our pedalboard:
                effected = board(chunk, f.samplerate, reset=False)
      
                # Write the output to our output file:
                o.write(effected)
    


# Function to convert text to speech
def text_to_speech(
          input_file,
          intent,
          output_directory,
          board, 
          sample_rate=48000,    #35000,
          speed_factor=1.15 #1.30
):
    """ Main function for TTS generation"""

    os.makedirs(output_directory, exist_ok=True)

    i=1
    # Read text from the input file
    with open(input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            content_type = row['content_type']
            text = row['text']

            # Generates an unique ID for each new file
            #unique_id = generate_id(content_type)
            output_audio_file = os.path.join(output_directory, f"{intent}_{i}.wav")  #   f"{unique_id}.mp3")
            i+=1            

            # Generate speech from text using Google Text-to-Speech (gTTS)  
            tts = gTTS(text, lang='en', tld='co.uk')
            tts.save("temp_audio.mp3")
    
            # Load the audio file
            audio = AudioSegment.from_mp3("temp_audio.mp3")
    
            # Resample the audio to the desired sample rate (35 kHz)
            #audio = audio.set_frame_rate(sample_rate)

            audio = audio._spawn(audio.raw_data, 
                         overrides={"frame_rate": int(audio.frame_rate * speed_factor)})

            audio = audio.set_frame_rate(sample_rate)

            ring_modulator("temp_audio.mp3", carrier_freq=100)

            voice_modification(board,output_audio_file)

            # Export the final audio file with the required sample rate
            #audio.export(output_audio_file, format="wav")

            # Delete the temporary file
            os.remove("temp_audio.mp3")
            os.remove("example1.wav")

            print(f"Speech saved to {output_audio_file}")



def main():

    audio_fname='audio_robot'

    # Example usage:
    intent = 'no-understand'
    input_file = 'no-understand_list.csv'  # Path to your input text file
    output_dir = f'../../content/{audio_fname}/no-understand'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    text_to_speech(input_file, intent, output_dir, board)

    intent = 'joke'
    input_file = 'joke_100_list.csv'  # Path to your input text file
    output_dir = f'../../content/{audio_fname}/100_jokes'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    text_to_speech(input_file, intent, output_dir, board)

    intent = 'riddle'
    input_file = 'riddle_100_list.csv'  # Path to your input text file
    output_dir = f'../../content/{audio_fname}/100_riddles'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    text_to_speech(input_file, intent, output_dir, board)

    intent = 'fact'
    input_file = 'fact_100_list.csv'  # Path to your input text file
    output_dir = f'../../content/{audio_fname}/100_facts'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    text_to_speech(input_file, intent, output_dir, board)
    
    intent = 'proverb'
    input_file = 'proverb_100_list.csv'  # Path to your input text file
    output_dir = f'../../content/{audio_fname}/100_proverbs'
    not os.path.exists(output_dir):
        os.makedirs(output_dir)
    text_to_speech(input_file, intent, output_dir, board)

    intent = 'tongue-twister'
    input_file = 'tongue-twister_100_list.csv'  # Path to your input text file
    output_dir = f'../../content/{audio_fname}/100_tongue-twisters'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    text_to_speech(input_file, intent, output_dir, board)

    intent = 'prefix'
    input_file = 'prefix_list.csv'  # Path to your input text file
    output_dir = f'../../content/{audio_fname}/prefix'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    text_to_speech(input_file, intent, output_dir, board)

    intent = 'hello'
    input_file = 'hello_list.csv'  # Path to your input text file
    output_dir = f'../../content/{audio_fname}/hello'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    text_to_speech(input_file, intent, output_dir, board)

    intent = 'bye'
    input_file = 'bye_list.csv'  # Path to your input text file
    output_dir = f'../../content/{audio_fname}/bye'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    text_to_speech(input_file, intent, output_dir, board)

    intent = 'story'
    input_file = 'story_4_list.csv'  # Path to your input text file
    output_dir = f'../../content/{audio_fname}/stories'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    text_to_speech(input_file, intent, output_dir, board)

if __name__ == '__main__':
    main()
