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

#def generate_id(content_type):
#    return f"{content_type}_{uuid.uuid4().hex[:8]}"

def voice_modification(
              board,
              output_audio_file
):
    
    audio, sr = librosa.load("temp_audio.mp3")

    # ADDS A ONE AND A HALF ECOND TAIL FOR REVERB TO BREATH
    audio = np.append(audio, [0.0]*33000)  

    # SHIFTES THE PITCH DOWN
    audio = librosa.effects.pitch_shift(audio, sr=sr, n_steps=-7.5)

    sf.write("tmp.wav", audio, sr)
    with AudioFile('tmp.wav') as f:
        
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

            voice_modification(board,output_audio_file)

            # Export the final audio file with the required sample rate
            #audio.export(output_audio_file, format="wav")

            # Delete the temporary file
            os.remove("temp_audio.mp3")

            print(f"Speech saved to {output_audio_file}")


board = Pedalboard([
    #Compressor(),
    Reverb(room_size=0.80, damping=0.25, dry_level=0.75, wet_level=0.25),
    Compressor(),
    
])


# Example usage:

intent = 'no-understand'
input_file = 'no-understand_list.csv'  # Path to your input text file
output_dir = '../../content/audio_demon/no-understand'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
text_to_speech(input_file, intent, output_dir, board)

intent = 'joke'
input_file = 'joke_100_list.csv'  # Path to your input text file
output_dir = '../../content/audio_demon/100_jokes'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
text_to_speech(input_file, intent, output_dir, board)

intent = 'riddle'
input_file = 'riddle_100_list.csv'  # Path to your input text file
output_dir = '../../content/audio_demon/100_riddles'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
text_to_speech(input_file, intent, output_dir, board)

intent = 'fact'
input_file = 'fact_100_list.csv'  # Path to your input text file
output_dir = '../../content/audio_demon/100_facts'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
text_to_speech(input_file, intent, output_dir, board)
    
intent = 'proverb'
input_file = 'proverb_100_list.csv'  # Path to your input text file
output_dir = '../../content/audio_demon/100_proverbs'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
text_to_speech(input_file, intent, output_dir, board)

intent = 'tongue-twister'
input_file = 'tongue-twister_100_list.csv'  # Path to your input text file
output_dir = '../../content/audio_demon/100_tongue-twisters'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
text_to_speech(input_file, intent, output_dir, board)

intent = 'prefix'
input_file = 'prefix_list.csv'  # Path to your input text file
output_dir = '../../content/audio_demon/prefix'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
text_to_speech(input_file, intent, output_dir, board)

intent = 'hello'
input_file = 'hello_list.csv'  # Path to your input text file
output_dir = '../../content/audio_demon/hello'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
text_to_speech(input_file, intent, output_dir, board)

intent = 'bye'
input_file = 'bye_list.csv'  # Path to your input text file
output_dir = '../../content/audio_demon/bye'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
text_to_speech(input_file, intent, output_dir, board)

intent = 'story'
input_file = 'story_4_list.csv'  # Path to your input text file
output_dir = '../../content/audio_demon/stories'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
text_to_speech(input_file, intent, output_dir, board)


