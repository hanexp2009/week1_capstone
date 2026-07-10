import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from song_input import mp3_input
from spectrogram import make_spectrogram
from fingerprint import find_peaks, make_fgp
from database import reset, add


RAW_DIR = Path("data/raw")
DATABASE_SECONDS = 60


def fingerprints_from_samples(samples, sample_rate):
    log_spec, freqs, times = make_spectrogram(samples, sample_rate)
    peaks = find_peaks(log_spec, percentile=75)
    return make_fgp(peaks)


song_paths = sorted(RAW_DIR.glob("*/*.mp3"))

print(f"found songs: {len(song_paths)}")

if not song_paths:
    raise FileNotFoundError("No mp3 files found under data/raw/*/*.mp3")

reset()

for idx, path in enumerate(song_paths):
    genre = path.parent.name
    song_id = f"song_{idx + 1:02d}"
    song_name = f"{genre}_{path.stem}"

    print(f"adding {song_id}: {song_name}")

    samples, sample_rate = mp3_input(str(path))
    known_song = samples[:DATABASE_SECONDS * sample_rate]
    fingerprints = fingerprints_from_samples(known_song, sample_rate)

    add(fingerprints, song_id, song_name)

print("database built")