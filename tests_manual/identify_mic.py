import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import math
import time

from song_input import mic_input
from spectrogram import make_spectrogram
from fingerprint import find_peaks, make_fgp
from match import query_details


LISTEN_TIME = 10


def fingerprints_from_samples(samples, sample_rate):
    log_spec, freqs, times = make_spectrogram(samples, sample_rate)
    peaks = find_peaks(log_spec, percentile=75)
    return make_fgp(peaks)


def confidence_score(best_count, second_count):
    if best_count <= 0:
        return 0.0

    count_score = min(best_count / 100, 1.0)

    if second_count <= 0:
        ratio_score = 1.0
    else:
        ratio = best_count / second_count
        ratio_score = min(max(math.log10(max(ratio, 1)), 0), 1.0)

    return round(100 * (0.4 * count_score + 0.6 * ratio_score), 2)


def confidence_label(score):
    if score >= 80:
        return "high"
    if score >= 50:
        return "medium"
    if score >= 25:
        return "low"
    return "very low"


input("Open the noisy clip and get ready to play it. Press Enter to start countdown.")

for i in range(3, 0, -1):
    print(i)
    time.sleep(1)

print(f"Recording for {LISTEN_TIME} seconds...")
samples, sample_rate = mic_input(LISTEN_TIME)

print("Processing...")
query_fgp = fingerprints_from_samples(samples, sample_rate)

best_song, best_count, counts = query_details(query_fgp)

if best_song is None:
    print("No match found.")
    raise SystemExit

top = counts.most_common(5)
second_count = top[1][1] if len(top) > 1 else 0
ratio = best_count / second_count if second_count else float("inf")

conf = confidence_score(best_count, second_count)
label = confidence_label(conf)

print()
print("Prediction:", best_song)
print("Best count:", best_count)
print("Second count:", second_count)
print("Ratio:", round(ratio, 2))
print("Confidence:", conf, label)
print("Top 5:", top)