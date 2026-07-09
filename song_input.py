import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Audio, display
from microphone import record_audio
from typing import Tuple
import sounddevice as sd
import librosa

def mic_input(listen_time):
    frames, sample_rate = record_audio(listen_time)
    samples = np.hstack([np.frombuffer(i, np.int16) for i in frames])
    return samples
def mp3_input(file_path):
    samples, sample_rate = librosa.load(file_path, sr=None)
    return samples, sample_rate




