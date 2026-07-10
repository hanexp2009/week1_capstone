import numpy as np
import librosa
from microphone import record_audio

def mic_input(listen_time):
    frames, sample_rate = record_audio(listen_time)
    samples = np.hstack([np.frombuffer(frame, np.int16) for frame in frames])
    samples = samples.astype(np.float32)/32768
    return samples, sample_rate


def mp3_input(file_path, sample_rate=44100):
    samples, sample_rate = librosa.load(file_path, sr=sample_rate, mono=True)
    return samples.astype(np.float32), sample_rate