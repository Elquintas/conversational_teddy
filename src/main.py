import os
import sys
import yaml
import json
import time
import wave
import nemo
import copy
import torch
import random
import logging
import librosa
import logging
import numpy as np
import pyaudio as pa
import matplotlib.pyplot as plt
import nemo.collections.asr as nemo_asr

from functools import partial
from omegaconf import OmegaConf
from torch.utils.data import DataLoader

from utils.nemo_utils import AudioDataLayer, FrameASR, infer_signal
from utils.audio_utils import record_audio, play_random_sound, play_sound
from logic_manager import audio_process

from nemo.core.neural_types import NeuralType, AudioSignal, LengthsType



# Adds the root directory of the project to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Creates shared object (dict), for exit condition
shared_state = {'exit_cond': False}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# KWS Reference:
# https://github.com/NVIDIA/NeMo/blob/main/tutorials/asr/Online_Offline_Speech_Commands_Demo.ipynb


def load_config(file_path):
    """
    Loads config file
    """
    
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config

#CONFIG_PATH = os.getenv('CONFIG_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml"))
CONFIG_PATH = os.getenv('CONFIG_PATH', None)
CONFIG = load_config(CONFIG_PATH)


def callback(in_data,
             frame_count, 
             time_info, 
             status, 
             vad, 
             mbn,
             vad_threshold
):
    """
    Callback function for streaming audio and performing inference
    """   
    
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


def main():

    # PARAMETERS
    SAMPLE_RATE = CONFIG['KWS']['samplerate']     #16000

    # VAD THRESHOLD - THE HIGHER THE LESS SENSITIVE THE VAD
    # 0.85 if client is a macbook pro
    # 0.9* if client is a raspberry pi with a small mic
    vad_threshold = CONFIG['KWS']['vad_threshold']   #0.9 # 0.85 #0.8

    #STEP = 0.1
    #WINDOW_SIZE = 0.25 #0.15
    #mbn_WINDOW_SIZE = 1

    STEP=CONFIG['KWS']['step_size']     #0.5
    WINDOW_SIZE=CONFIG['KWS']['vad_window_size'] #0.5
    mbn_WINDOW_SIZE=CONFIG['KWS']['mbn_window_size']   #1.5
    CHANNELS = CONFIG['KWS']['channels'] #1
    FRAME_LEN=STEP # use step of vad inference as frame len
    CHUNK_SIZE=int(STEP * SAMPLE_RATE)

    content_file=CONFIG['content']['content_file']  #'../content/teddy_content_robot.json'
    with open(content_file, 'r') as file:
        content_data = json.load(file)

    # Nemo pretrained models
    asr_model = nemo_asr.models.ASRModel.from_pretrained(CONFIG['models']['asr_model'])
    mbn_model = nemo_asr.models.EncDecClassificationModel.from_pretrained(CONFIG['models']['mbn_model'])
    vad_model = nemo_asr.models.EncDecClassificationModel.from_pretrained(CONFIG['models']['vad_model'])

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

            # Plays random 'bye' audio file
            bye_file_list=content_data['intentions']['bye']['options']
            play_random_sound(bye_file_list)

            logger.info('Exiting Teddy.')
            sys.exit()

        time.sleep(0.5)
        
        # Plays random 'bye' audio file
        hello_file_list=content_data['intentions']['hello']['options']
        play_random_sound(hello_file_list)               

        # Records audio clip to send to server
        logger.info('Recording audio...')
        tmp_audio = record_audio(
                        audio_dur=CONFIG['rec_duration'],
                        fs=CONFIG['rec_samplerate'],
                        channels=CONFIG['rec_channels']
                        )
        logger.info('Audio saved to {}'.format(tmp_audio))
        
        response_file, intent = audio_process(tmp_audio,asr_model,content_data)     
        
        if os.path.exists(tmp_audio):
            os.remove(tmp_audio)

        if os.path.exists(response_file):
            # plays occasionally a random prefix
            if random.random() < 0.75 and intent != "no-understand":
                time.sleep(0.3)
                prefix_file_list=content_data['intentions']['hello']['options']
                play_random_sound(prefix_file_list)
            
            time.sleep(0.3)
            play_sound(response_file)
        else:
            logger.warning("Audio file not found.")

        # Sets up streaming flag for continuity
        streaming = True           
        shared_state['streaming'] = True
        
if __name__ == '__main__':
    main()
