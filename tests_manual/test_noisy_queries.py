import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np

from song_input import mp3_input
from spectrogram import make_spectrogram
from fingerprint import find_peaks, make_fgp
from database import reset, add
from match import query_details


def fingerprints_from_samples(samples, sample_rate):
    log_spec, freqs, times = make_spectrogram(samples, sample_rate)
    peaks = find_peaks(log_spec, percentile=75)
    return make_fgp(peaks)


def add_noise(samples, snr_db, seed=0):
    rng = np.random.default_rng(seed)

    signal_power = np.mean(samples ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))

    noise = rng.normal(0, np.sqrt(noise_power), size=samples.shape)
    noisy = samples + noise

    return np.clip(noisy, -1, 1).astype(np.float32)


samples, sample_rate = mp3_input("data/raw/test_song.mp3")

# Build database from a clean 60-second segment
known_song = samples[:60 * sample_rate]
known_fgp = fingerprints_from_samples(known_song, sample_rate)

reset()
add(
    known_fgp,
    song_ID="song_1",
    song_name="test_song",
)

durations = [5, 10, 15]
snrs = [30, 20, 10, 5, 0]

start_sec = 30

print("duration,snr_db,best_song,best_count,second_count,ratio")

for duration in durations:
    clean_clip = samples[start_sec * sample_rate : (start_sec + duration) * sample_rate]

    for snr in snrs:
        noisy_clip = add_noise(clean_clip, snr_db=snr, seed=duration * 100 + snr)
        query_fgp = fingerprints_from_samples(noisy_clip, sample_rate)

        best_song, best_count, counts = query_details(query_fgp)
        top = counts.most_common(5)
        second_count = top[1][1] if len(top) > 1 else 0
        ratio = best_count / second_count if second_count else float("inf")

        print(f"{duration},{snr},{best_song},{best_count},{second_count},{ratio:.2f}")