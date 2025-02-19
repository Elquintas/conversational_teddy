import numpy as np
import pyaudio as pa
import os, time
import librosa
import IPython.display as ipd
import matplotlib.pyplot as plt
import pyaudio
import time
import wave
import nemo
import socket
import nemo.collections.asr as nemo_asr

from omegaconf import OmegaConf
import copy

from nemo.core.classes import IterableDataset
from nemo.core.neural_types import NeuralType, AudioSignal, LengthsType
import torch
from torch.utils.data import DataLoader

# Data layer used to pass audio signal
class AudioDataLayer(IterableDataset):
    @property
    def output_types(self):
        return {
            'audio_signal': NeuralType(('B', 'T'), AudioSignal(freq=self._sample_rate)),
            'a_sig_length': NeuralType(tuple('B'), LengthsType()),
        }

    def __init__(self, sample_rate):
        super().__init__()
        self._sample_rate = sample_rate
        self.output = True
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.output:
            raise StopIteration
        self.output = False
        return torch.as_tensor(self.signal, dtype=torch.float32), \
               torch.as_tensor(self.signal_shape, dtype=torch.int64)
        
    def set_signal(self, signal):
        self.signal = signal.astype(np.float32)/32768.
        self.signal_shape = self.signal.size
        self.output = True

    def __len__(self):
        return 1

def infer_signal(model, signal, data_layer, data_loader):
    data_layer.set_signal(signal)
    batch = next(iter(data_loader))
    audio_signal, audio_signal_len = batch
    audio_signal, audio_signal_len = audio_signal.to(model.device), audio_signal_len.to(model.device)
    logits = model.forward(input_signal=audio_signal, input_signal_length=audio_signal_len)
    return logits


# class for streaming frame-based ASR
# 1) use reset() method to reset FrameASR's state
# 2) call transcribe(frame) to do ASR on
#    contiguous signal's frames
class FrameASR:

    def __init__(self, model_definition,model,data_layer,data_loader,
                 frame_len=2, frame_overlap=2.5,
                 offset=0):
        '''
        Args:
          frame_len (seconds): Frame's duration
          frame_overlap (seconds): Duration of overlaps before and after current frame.
          offset: Number of symbols to drop for smooth streaming.
        '''
        self.model = model
        self.data_layer = data_layer
        self.data_loader = data_loader

        self.task = model_definition['task']
        self.vocab = list(model_definition['labels'])

        self.sr = model_definition['sample_rate']
        self.frame_len = frame_len
        self.n_frame_len = int(frame_len * self.sr)
        self.frame_overlap = frame_overlap
        self.n_frame_overlap = int(frame_overlap * self.sr)
        timestep_duration = model_definition['AudioToMFCCPreprocessor']['window_stride']
        for block in model_definition['JasperEncoder']['jasper']:
            timestep_duration *= block['stride'][0] ** block['repeat']
        self.buffer = np.zeros(shape=2*self.n_frame_overlap + self.n_frame_len,
                               dtype=np.float32)
        self.offset = offset
        self.reset()

    @torch.no_grad()
    def _decode(self, frame, offset=0):
        assert len(frame)==self.n_frame_len
        self.buffer[:-self.n_frame_len] = self.buffer[self.n_frame_len:]
        self.buffer[-self.n_frame_len:] = frame

        if self.task == 'mbn':
            logits = infer_signal(self.model, self.buffer, self.data_layer,
                    self.data_loader).to('cpu').numpy()[0]
            decoded = self._mbn_greedy_decoder(logits, self.vocab)

        elif self.task == 'vad':
            logits = infer_signal(self.model, self.buffer, self.data_layer,
                    self.data_loader).to('cpu').numpy()[0]
            decoded = self._vad_greedy_decoder(logits, self.vocab)

        else:
            raise("Task should either be of mbn or vad!")

        return decoded[:len(decoded)-offset]

    def transcribe(self, frame=None,merge=False):
        if frame is None:
            frame = np.zeros(shape=self.n_frame_len, dtype=np.float32)
        if len(frame) < self.n_frame_len:
            frame = np.pad(frame, [0, self.n_frame_len - len(frame)], 'constant')
        unmerged = self._decode(frame, self.offset)
        return unmerged


    def reset(self):
        '''
        Reset frame_history and decoder's state
        '''
        self.buffer=np.zeros(shape=self.buffer.shape, dtype=np.float32)
        self.mbn_s = []
        self.vad_s = []

    @staticmethod
    def _mbn_greedy_decoder(logits, vocab):
        mbn_s = []
        if logits.shape[0]:
            class_idx = np.argmax(logits)
            class_label = vocab[class_idx]
            mbn_s.append(class_label)
        return mbn_s


    @staticmethod
    def _vad_greedy_decoder(logits, vocab):
        vad_s = []
        if logits.shape[0]:
            probs = torch.softmax(torch.as_tensor(logits), dim=-1)
            probas, preds = torch.max(probs, dim=-1)
            vad_s = [preds.item(), str(vocab[preds]), probs[0].item(), probs[1].item(), str(logits)]
        return vad_s

