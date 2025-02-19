import os
import sys
import json
import time
import wave
import nemo
import copy
import torch
import random
import socket
import logging
import librosa
import logging
import numpy as np
import pyaudio as pa
import soundfile as sf
import sounddevice as sd
import IPython.display as ipd
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavfile
import nemo.collections.asr as nemo_asr

from functools import partial
from omegaconf import OmegaConf
from torch.utils.data import DataLoader
from nemo.core.classes import IterableDataset
from nemo_utils import AudioDataLayer, FrameASR, infer_signal
from nemo.core.neural_types import NeuralType, AudioSignal, LengthsType

from logic_standalone import audio_process

# Creates shared object (dict), for exit condition
shared_state = {'exit_cond': False}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# KWS Reference:
# https://github.com/NVIDIA/NeMo/blob/main/tutorials/asr/Online_Offline_Speech_Commands_Demo.ipynb


"""
Function to record audio after wake-word is activated
"""
def record_audio(
    file_name='./audio/tmp_audio.wav', 
    audio_dur=4, 
    fs=44100, 
    channels=1, 
    dtype='int16'):
    
    #print("[INFO] : Recording audio...")
    logger.info('Recording audio...')
    audio_data = sd.rec(
                        int(audio_dur * fs), 
                        samplerate=fs, 
                        channels=channels, 
                        dtype=dtype
                        )
    sd.wait()  # Wait until recording is finished

    wavfile.write(file_name, fs, audio_data)
    logger.info('Audio saved to {}'.format(file_name))


"""
Callback function for streaming audio and performing inference
"""
def callback(in_data,
             frame_count, 
             time_info, 
             status, 
             vad, 
             mbn,
             vad_threshold):
   
    signal = np.frombuffer(in_data, dtype=np.int16)
    vad_result = vad.transcribe(signal)
    mbn_result = mbn.transcribe(signal)

    stop_stream=False

    if len(vad_result):
     # if speech prob is higher than threshold, we decide it contains 
     # speech utterance and activate MatchBoxNet
        
        if vad_result[3] >= vad_threshold:
            print(mbn_result) # print mbn result when speech present

            if mbn_result[0]=='marvin': 
                stop_stream=True

            if mbn_result[0]=='stop': 
                stop_stream=True
                shared_state['exit_cond'] = True          
                
        else:
            print("no-speech")

    if stop_stream:
    #if shared_state['streaming'] == False:
        return (in_data, pa.paAbort)

    return (in_data, pa.paContinue)


"""
Plays one of the random hello audios
"""
def random_hello_sound(content_data):
    
    option_list = content_data['intentions']['hello']['options']
    filename = random.choice(option_list)['file_path']
    
    #hello_dir = './content/audio/hello/'
    #files = [f for f in os.listdir(hello_dir) \
    #         if os.path.isfile(os.path.join(hello_dir,f))]
    #play_sound(hello_dir+random.choice(files))

    play_sound(filename)

"""
Plays one of the random bye audios
"""
def random_bye_sound(content_data):

    option_list = content_data['intentions']['bye']['options']
    filename = random.choice(option_list)['file_path']

    #bye_dir = './content/audio/bye/'
    #files = [f for f in os.listdir(bye_dir) \
    #         if os.path.isfile(os.path.join(bye_dir,f))]
    #play_sound(bye_dir+random.choice(files))

    play_sound(filename)
    

"""
Base function to play any sound
"""
def play_sound(filename):
    
    data, fs = sf.read(filename, dtype='float32')  
    
    # Ignores the first 100 samples due to loud clicking sound
    sd.play(data[100:], 22050) #48000) #35000)
    status = sd.wait()

"""
Plays a prefix once we get a response from the logic module
"""
def play_prefix(data):
    
    option_list = data['intentions']['prefix']['options']
    ret_file = random.choice(option_list)['file_path']
    
    play_sound(ret_file)

def main():

    # PARAMETERS
    SAMPLE_RATE = 16000

    # VAD THRESHOLD - THE HIGHER THE LESS SENSITIVE THE VAD
    # 0.85 if client is a macbook pro
    # 0.9* if client is a raspberry pi with a small mic
    vad_threshold = 0.9 # 0.85   #0.8

    #STEP = 0.1
    #WINDOW_SIZE = 0.25 #0.15
    #mbn_WINDOW_SIZE = 1

    STEP=0.5
    WINDOW_SIZE=0.5
    mbn_WINDOW_SIZE=1.5

    CHANNELS = 1
    RATE = SAMPLE_RATE
    FRAME_LEN = STEP # use step of vad inference as frame len
    CHUNK_SIZE = int(STEP * RATE)

    content_file = '/home/squintas/git_teddy/standalone/content/teddy_content_robot.json'
    with open(content_file, 'r') as file:
        content_data = json.load(file)



    # ASR MODULES
    #asr_model = nemo_asr.models.ASRModel.from_pretrained("stt_en_conformer_transducer_medium")
    #asr_model = nemo_asr.models.ASRModel.from_pretrained("stt_en_conformer_transducer_small")
    asr_model = nemo_asr.models.ASRModel.from_pretrained("stt_en_conformer_ctc_small")
    #asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_name="stt_en_citrinet_256")
    #asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name="QuartzNet15x5Base-En")
    
    # KEYWORD SPOTTING MODULES
    mbn_model = nemo_asr.models.EncDecClassificationModel.from_pretrained("commandrecognition_en_matchboxnet3x1x64_v2")
    #vad_model = nemo_asr.models.EncDecClassificationModel.from_pretrained('vad_marblenet')
    vad_model = nemo_asr.models.EncDecClassificationModel.from_pretrained("vad_multilingual_marblenet")

    # Preserve a copy of the full config
    vad_cfg = copy.deepcopy(vad_model._cfg)
    mbn_cfg = copy.deepcopy(mbn_model._cfg)

    labels = mbn_cfg.labels
    
    # Set model to inference mode
    mbn_model.eval()
    vad_model.eval()

    data_layer = AudioDataLayer(sample_rate=mbn_cfg.train_ds.sample_rate)
    data_loader = DataLoader(data_layer, batch_size=1, collate_fn=data_layer.collate_fn)


    vad = FrameASR(model_definition = {
                   'task': 'vad',
                   'sample_rate': SAMPLE_RATE,
                   'AudioToMFCCPreprocessor': vad_cfg.preprocessor,
                   'JasperEncoder': vad_cfg.encoder,
                   'labels': vad_cfg.labels
               },model=vad_model,data_layer=data_layer,data_loader=data_loader,
               frame_len=FRAME_LEN, frame_overlap=(WINDOW_SIZE - FRAME_LEN) / 2, 
               offset=0)

    mbn = FrameASR(model_definition = {
                   'task': 'mbn',
                   'sample_rate': SAMPLE_RATE,
                   'AudioToMFCCPreprocessor': mbn_cfg.preprocessor,
                   'JasperEncoder': mbn_cfg.encoder,
                   'labels': mbn_cfg.labels
               },model=mbn_model,data_layer=data_layer,data_loader=data_loader,
               frame_len=FRAME_LEN, frame_overlap = (mbn_WINDOW_SIZE-FRAME_LEN)/2,
               offset=0)

    vad.reset()
    mbn.reset()

    # Function wrapper for callback function
    # Used to pass vbn and mbn models as arguments
    wrapped_callback = partial(callback, 
                               vad=vad, 
                               mbn=mbn,
                               vad_threshold=vad_threshold)

    # Setup input device
    p = pa.PyAudio()
    print('[INFO] : Available audio input devices:')
    input_devices = []
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev.get('maxInputChannels'):
            input_devices.append(i)
            print(i, dev.get('name'))

    if len(input_devices):
        for dev in input_devices:
            if int(dev)==17:
                dev_idx=17
                break
            elif int(dev)==3:
                dev_idx=3
                break

    streaming = True
        
    while True:
        if not p==pa.PyAudio(): p = pa.PyAudio()
        if streaming:

            # streaming            
            stream = p.open(format=pa.paInt16,
                        channels=CHANNELS,
                        rate=SAMPLE_RATE,
                        input=True,
                        input_device_index=dev_idx,
                        stream_callback=wrapped_callback,
                        frames_per_buffer=CHUNK_SIZE)

            logger.info('Listening...')
            stream.start_stream()

            # Interrupt kernel and then speak for a few more 
            # words to exit the pyaudio loop !
            try:
                while stream.is_active():
                    time.sleep(0.1)
            finally:
                streaming=False
                stream.stop_stream()
                stream.close()
                p.terminate()
                logger.info('PyAudio stopped.')
                
        # Checks for exit condition
        if shared_state['exit_cond']:
            random_bye_sound(content_data)
            logger.info('Exiting Teddy.')
            sys.exit()

        time.sleep(0.5)        
        random_hello_sound(content_data)        

        # Records audio clip to send to server
        record_audio()
        
        # Sends audio clip to logic module
        tmp_audio = './audio/tmp_audio.wav'
        response_file, intent = audio_process(tmp_audio,asr_model,content_data)     

        if os.path.exists(response_file):
            
            # plays occasionally a random prefix
            if random.random() < 0.75 and intent != "no-understand":
                time.sleep(0.3)
                play_prefix(content_data)
            
            time.sleep(0.3)
            play_sound(response_file)
        else:
            logger.warning("Audio file not found.")

        # Sets up streaming flag for continuity
        streaming = True           
        shared_state['streaming'] = True
        
if __name__ == '__main__':
    main()
