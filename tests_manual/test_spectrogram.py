import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from song_input import mp3_input
from spectrogram import make_spectrogram

samples, sample_rate = mp3_input("data/raw/test_song.mp3")

# use only first 30 seconds for faster testing
samples = samples[:30 * sample_rate]

log_spec, freqs, times = make_spectrogram(samples, sample_rate)

print("log_spec type:", type(log_spec))
print("log_spec shape:", log_spec.shape)
print("freqs shape:", freqs.shape)
print("times shape:", times.shape)
print("log_spec min/max:", log_spec.min(), log_spec.max())