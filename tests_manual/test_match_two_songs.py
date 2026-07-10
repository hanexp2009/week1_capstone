import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from song_input import mp3_input
from spectrogram import make_spectrogram
from fingerprint import find_peaks, make_fgp
from database import reset, add
from match import query_details


def fingerprints_from_samples(samples, sample_rate):
    log_spec, freqs, times = make_spectrogram(samples, sample_rate)
    peaks = find_peaks(log_spec, percentile=75)
    return make_fgp(peaks)


def add_song_to_db(path, song_id, song_name):
    samples, sample_rate = mp3_input(path)
    known_song = samples[:60 * sample_rate]
    fingerprints = fingerprints_from_samples(known_song, sample_rate)
    add(fingerprints, song_ID=song_id, song_name=song_name)
    return samples, sample_rate


reset()

song1, sr1 = add_song_to_db("data/raw/test_song.mp3", "song_1", "test_song")
song2, sr2 = add_song_to_db("data/raw/test_song_2.mp3", "song_2", "test_song_2")

tests = [
    ("song_1 query", song1, sr1, "test_song"),
    ("song_2 query", song2, sr2, "test_song_2"),
]

for label, samples, sample_rate, expected in tests:
    query_clip = samples[30 * sample_rate : 40 * sample_rate]
    query_fgp = fingerprints_from_samples(query_clip, sample_rate)

    best_song, best_count, counts = query_details(query_fgp)
    top = counts.most_common(5)

    print(label)
    print("  expected:", expected)
    print("  predicted:", best_song)
    print("  best_count:", best_count)
    print("  top 5:", top)