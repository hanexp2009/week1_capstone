import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from song_input import mp3_input
from spectrogram import make_spectrogram
from fingerprint import find_peaks, make_fgp

samples, sample_rate = mp3_input("data/raw/test_song.mp3")

# use first 30 seconds for faster testing
samples = samples[:30 * sample_rate]

log_spec, freqs, times = make_spectrogram(samples, sample_rate)

peaks = find_peaks(log_spec)
fingerprints = make_fgp(peaks)

print("spectrogram shape:", log_spec.shape)
print("num peaks:", len(peaks))
print("num fingerprints:", len(fingerprints))
print("first 5 peaks:", peaks[:5])
print("first 5 fingerprints:", fingerprints[:5])