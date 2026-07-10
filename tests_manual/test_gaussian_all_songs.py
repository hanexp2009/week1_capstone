import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import csv
import math
import numpy as np

from song_input import mp3_input
from spectrogram import make_spectrogram
from fingerprint import find_peaks, make_fgp
from database import reset, add
from match import query_details


RAW_DIR = Path("data/raw")
OUT_PATH = Path("tests_manual/gaussian_all_songs_results.csv")

DATABASE_SECONDS = 60
START_SEC = 30

DURATIONS = [5, 10, 15]
SNRS = [30, 20, 10, 5, 0]

# Change to a number like 10 for quick testing.
# Set to None to use all songs.
LIMIT_SONGS = None


def fingerprints_from_samples(samples, sample_rate):
    log_spec, freqs, times = make_spectrogram(samples, sample_rate)
    peaks = find_peaks(log_spec, percentile=75)
    return make_fgp(peaks)


def add_gaussian_noise(samples, snr_db, seed=0):
    rng = np.random.default_rng(seed)

    signal_power = np.mean(samples ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))

    noise = rng.normal(0, np.sqrt(noise_power), size=samples.shape)
    noisy = samples + noise

    return np.clip(noisy, -1, 1).astype(np.float32)


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


def add_song_to_db(path, song_id, song_name):
    samples, sample_rate = mp3_input(str(path))

    known_song = samples[:DATABASE_SECONDS * sample_rate]
    fingerprints = fingerprints_from_samples(known_song, sample_rate)

    add(fingerprints, song_ID=song_id, song_name=song_name)

    return samples, sample_rate


song_paths = sorted(RAW_DIR.glob("*/*.mp3"))

if LIMIT_SONGS is not None:
    song_paths = song_paths[:LIMIT_SONGS]

print(f"found songs: {len(song_paths)}")

if not song_paths:
    raise FileNotFoundError("No mp3 files found under data/raw/*/*.mp3")

reset()

loaded = []

print("building database...")

for idx, path in enumerate(song_paths):
    genre = path.parent.name
    song_id = f"song_{idx + 1:02d}"
    song_name = f"{genre}_{path.stem}"

    print(f"  adding {song_id}: {song_name}")

    samples, sample_rate = add_song_to_db(path, song_id, song_name)
    loaded.append((song_name, genre, samples, sample_rate))

print("running noisy tests...")

rows = []
summary = {}

total = 0
correct = 0

for song_idx, (expected, genre, samples, sample_rate) in enumerate(loaded):
    for duration in DURATIONS:
        start = START_SEC * sample_rate
        end = (START_SEC + duration) * sample_rate
        clean_clip = samples[start:end]

        if len(clean_clip) < duration * sample_rate:
            print(f"skipping short clip: {expected}, duration={duration}")
            continue

        for snr in SNRS:
            noisy_clip = add_gaussian_noise(
                clean_clip,
                snr_db=snr,
                seed=song_idx * 10000 + duration * 100 + snr,
            )

            query_fgp = fingerprints_from_samples(noisy_clip, sample_rate)
            best_song, best_count, counts = query_details(query_fgp)

            top = counts.most_common(5)
            second_count = top[1][1] if len(top) > 1 else 0
            ratio = best_count / second_count if second_count else float("inf")

            conf = confidence_score(best_count, second_count)
            label = confidence_label(conf)

            is_correct = best_song == expected

            total += 1
            correct += is_correct

            key = (duration, snr)
            if key not in summary:
                summary[key] = [0, 0]
            summary[key][0] += is_correct
            summary[key][1] += 1

            row = {
                "song": expected,
                "genre": genre,
                "duration": duration,
                "snr_db": snr,
                "expected": expected,
                "predicted": best_song,
                "correct": is_correct,
                "best_count": best_count,
                "second_count": second_count,
                "ratio": round(ratio, 2),
                "confidence": conf,
                "label": label,
            }

            rows.append(row)

            print(
                f"{expected},{duration},{snr},{best_song},{is_correct},"
                f"{best_count},{second_count},{ratio:.2f},{conf},{label}"
            )

print()
print(f"overall accuracy: {correct}/{total} = {correct / total:.3f}")

print()
print("summary by duration/SNR:")
print("duration,snr_db,correct,total,accuracy")

for duration in DURATIONS:
    for snr in SNRS:
        c, t = summary.get((duration, snr), [0, 0])
        acc = c / t if t else 0
        print(f"{duration},{snr},{c},{t},{acc:.3f}")

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(OUT_PATH, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print()
print(f"saved results to {OUT_PATH}")