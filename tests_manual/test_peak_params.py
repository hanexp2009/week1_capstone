import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from song_input import mp3_input
from spectrogram import make_spectrogram
from fingerprint import find_peaks, make_fgp

samples, sample_rate = mp3_input("data/raw/test_song.mp3")
samples = samples[:30 * sample_rate]

log_spec, freqs, times = make_spectrogram(samples, sample_rate)

for p in [70, 75, 80, 85, 90]:
    peaks = find_peaks(log_spec, percentile=p)
    fingerprints = make_fgp(peaks)

    print("percentile:", p)
    print("  peaks:", len(peaks))
    print("  fingerprints:", len(fingerprints))