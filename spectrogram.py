import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from song_input import mic_input

def make_spectrogram(samples, sampling_rate=44100):
    S, freqs, times = mlab.specgram(
        samples,
        NFFT=4096,
        Fs=sampling_rate,
        window=mlab.window_hanning,
        noverlap=4096 // 2,
        mode='magnitude',
    )
    return S, freqs, times


