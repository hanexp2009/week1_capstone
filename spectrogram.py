import numpy as np
import matplotlib.mlab as mlab

def make_spectrogram(samples, sample_rate, nfft=4096, noverlap=2048):
    spec, freqs, times = mlab.specgram(
        samples,
        NFFT=nfft,
        Fs=sample_rate,
        window=mlab.window_hanning,
        noverlap=noverlap,
    )
    spec = np.clip(spec, 1e-20, None)
    log_spec = np.log(spec)
    return log_spec, freqs, times