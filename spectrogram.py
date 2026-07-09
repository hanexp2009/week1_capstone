import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from song_input import mic_input

recorded_audio = mic_input(5)
sampling_rate = 44100
fig, ax = plt.subplots()
S, freqs, times, im = ax.specgram(
    recorded_audio,
    NFFT=4096,
    Fs=sampling_rate,
    window=mlab.window_hanning,
    noverlap=4096 // 2,
    mode='magnitude',
    scale="dB"
)
fig.colorbar(im)

ax.set_xlabel("Time [seconds]")
ax.set_ylabel("Frequency (Hz)")
ax.set_title("Spectrogram of Recording")
ax.set_ylim(0, 4000);
plt.show()