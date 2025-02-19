import random
import re
import os
import sys
import socket
import signal
import wave
import time
import logging
import numpy as np
import nemo.collections.asr as nemo_asr

running=True
logger=logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,  # Set the logging level to INFO
                    format='%(asctime)s - %(levelname)s - %(message)s')

"""
Function used to process the recorded audio file
"""
def audio_process(filename, asr_model, content_data):
    
    # Transcribes recorded audio file
    prompt = transcribe(asr_model,filename)
    
    # Applies logic to the transcription
    audio_response = teddy_server_logic(prompt,content_data)    
    
    return audio_response


"""
Function used to transcribe audio data received from the client
return text transcription
"""
def transcribe(asr_model,filename):
    
    logger.info('Beginning transcription...')
    transcript = asr_model.transcribe([filename])
    text = transcript[0]  #[0]

    if text: 
        logger.info("Transcribed audio - {}".format([text]))
    else: 
        logger.warning("Error while transcribing.")
        text = ['']

    return text

"""
Logic function for teddy interaction based on simple regex expressions.

Teddy currently supports 6 main intentions:
	- Story
	- Joke
	- Fact
	- Riddle
    - proverb
    - tongue twister

"""
def teddy_server_logic(prompt, data):
   
    option_list = data['intentions']['no-understand']['options']
    ret_file = random.choice(option_list)['file_path']
   
    if prompt == ['']:
        return ret_file, "no-understand"
   
    story_pattern = r"(story|tale)"
    joke_pattern = r"(joke|laugh)"
    fact_pattern = r"(fact|effect|affect)"
    riddle_pattern = r"(riddle|ribal|rival)"
    proverb_pattern = r"(proverb|phrase|wisdom|traditional|prover)"
    tonguetwister_pattern = r"(tongue|twister|toister|tonggue|twistter)"
    
    if re.search(story_pattern, prompt):
        option_list = data['intentions']['story']['options']
        return random.choice(option_list)['file_path'], "story"
       
    elif re.search(joke_pattern,prompt):  
        option_list = data['intentions']['joke']['options']       
        return random.choice(option_list)['file_path'], "joke"
               
    elif re.search(fact_pattern,prompt):  
        option_list = data['intentions']['fact']['options']       
        return random.choice(option_list)['file_path'], "fact"
             
    elif re.search(riddle_pattern,prompt):  
        option_list = data['intentions']['riddle']['options']
        return random.choice(option_list)['file_path'], "riddle"    

    elif re.search(proverb_pattern,prompt):  
        option_list = data['intentions']['proverb']['options']
        return random.choice(option_list)['file_path'], "proverb"
        
    elif re.search(tonguetwister_pattern,prompt):  
        option_list = data['intentions']['tongue-twister']['options']
        return random.choice(option_list)['file_path'], "tonguetwister"
    
    
    return ret_file, "no-understand"
