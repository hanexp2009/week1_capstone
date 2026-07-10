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
NOISE_DIR = Path("data/noise/wav")
OUT_PATH = Path("tests_manual/real_noise_all_songs_results.csv")

DATABASE_SECONDS = 60
START_SEC = 30

DURATIONS = [5, 10, 15]
SNRS = [30, 20, 10, 5, 0]

# Set to 10 for a quick test, None for all 35 songs.
LIMIT_SONGS = None


def fingerprints_from_samples(samples, sample_rate):
    log_spec, freqs, times = make_spectrogram(samples, sample_rate)
    peaks = find_peaks(log_spec, percentile=75)
    return make_fgp(peaks)


def mix_real_noise(clean_clip, noise_samples, snr_db, seed=0):
    rng = np.random.default_rng(seed)

    if len(noise_samples) < len(clean_clip):
        reps = int(np.ceil(len(clean_clip) / len(noise_samples)))
        noise_samples = np.tile(noise_samples, reps)

    start = rng.integers(0, len(noise_samples) - len(clean_clip) + 1)
    noise_clip = noise_samples[start:start + len(clean_clip)]

    signal_power = np.mean(clean_clip ** 2) + 1e-12
    noise_power = np.mean(noise_clip ** 2) + 1e-12

    target_noise_power = signal_power / (10 ** (snr_db / 10))
    scale = np.sqrt(target_noise_power / noise_power)

    mixed = clean_clip + scale * noise_clip
    return np.clip(mixed, -1, 1).astype(np.float32)


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
noise_paths = sorted(NOISE_DIR.glob("*.wav"))

if LIMIT_SONGS is not None:
    song_paths = song_paths[:LIMIT_SONGS]

print(f"found songs: {len(song_paths)}")
print(f"found noise clips: {len(noise_paths)}")

if not song_paths:
    raise FileNotFoundError("No mp3 files found under data/raw/*/*.mp3")

if not noise_paths:
    raise FileNotFoundError("No wav files found under data/noise/wav/*.wav")

reset()

loaded_songs = []

print("building database...")

for idx, path in enumerate(song_paths):
    genre = path.parent.name
    song_id = f"song_{idx + 1:02d}"
    song_name = f"{genre}_{path.stem}"

    print(f"  adding {song_id}: {song_name}")

    samples, sample_rate = add_song_to_db(path, song_id, song_name)
    loaded_songs.append((song_name, genre, samples, sample_rate))

print("loading noise files...")

loaded_noise = []

for path in noise_paths:
    noise_samples, noise_sr = mp3_input(str(path), sample_rate=44100)
    loaded_noise.append((path.stem, noise_samples))

print("running real-noise tests...")

rows = []
summary = {}

total = 0
correct = 0

print("song,genre,noise,duration,snr_db,expected,predicted,correct,best_count,second_count,ratio,confidence,label")

for song_idx, (expected, genre, samples, sample_rate) in enumerate(loaded_songs):
    for noise_idx, (noise_name, noise_samples) in enumerate(loaded_noise):
        for duration in DURATIONS:
            start = START_SEC * sample_rate
            end = (START_SEC + duration) * sample_rate
            clean_clip = samples[start:end]

            if len(clean_clip) < duration * sample_rate:
                print(f"skipping short clip: {expected}, duration={duration}")
                continue

            for snr in SNRS:
                noisy_clip = mix_real_noise(
                    clean_clip,
                    noise_samples,
                    snr_db=snr,
                    seed=song_idx * 100000 + noise_idx * 10000 + duration * 100 + snr,
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

                key = (noise_name, duration, snr)
                if key not in summary:
                    summary[key] = [0, 0]
                summary[key][0] += is_correct
                summary[key][1] += 1

                row = {
                    "song": expected,
                    "genre": genre,
                    "noise": noise_name,
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
                    f"{expected},{genre},{noise_name},{duration},{snr},"
                    f"{expected},{best_song},{is_correct},"
                    f"{best_count},{second_count},{ratio:.2f},{conf},{label}"
                )

print()
print(f"overall accuracy: {correct}/{total} = {correct / total:.3f}")

print()
print("summary by noise/duration/SNR:")
print("noise,duration,snr_db,correct,total,accuracy")

for noise_name, _ in loaded_noise:
    for duration in DURATIONS:
        for snr in SNRS:
            c, t = summary.get((noise_name, duration, snr), [0, 0])
            acc = c / t if t else 0
            print(f"{noise_name},{duration},{snr},{c},{t},{acc:.3f}")

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(OUT_PATH, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print()
print(f"saved results to {OUT_PATH}")
