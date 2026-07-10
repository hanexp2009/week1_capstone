import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from song_input import mp3_input
from spectrogram import make_spectrogram
from fingerprint import find_peaks, make_fgp
from database import reset, add, load, loadSongs
from match import query, query_details


def fingerprints_from_samples(samples, sample_rate):
    log_spec, freqs, times = make_spectrogram(samples, sample_rate)
    peaks = find_peaks(log_spec, percentile=75)
    return make_fgp(peaks)


samples, sample_rate = mp3_input("data/raw/test_song.mp3")

# use first 60 seconds as the known database song
known_song = samples[:60 * sample_rate]

# use a 10-second clip from inside that known song
query_clip = samples[30 * sample_rate : 40 * sample_rate]

known_fgp = fingerprints_from_samples(known_song, sample_rate)
query_fgp = fingerprints_from_samples(query_clip, sample_rate)

reset()

add(
    known_fgp,
    song_ID="song_1",
    song_name="test_song",
)

print("database keys:", len(load()))
print("songs:", loadSongs())
print("query fingerprints:", len(query_fgp))

print("simple result:", query(query_fgp))

best_song, best_count, counts = query_details(query_fgp)

print("detailed result:", best_song)
print("best count:", best_count)
print("top 5:", counts.most_common(5))