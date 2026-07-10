import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from song_input import mp3_input

samples, sample_rate = mp3_input("data/raw/test_song.mp3")

print("type:", type(samples))
print("shape:", samples.shape)
print("dtype:", samples.dtype)
print("sample_rate:", sample_rate)
print("min/max:", samples.min(), samples.max())
print("duration:", len(samples) / sample_rate)