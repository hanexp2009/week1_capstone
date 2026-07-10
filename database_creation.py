from spectrogram import make_spectrogram
import database
from fingerprint import find_peaks, make_fgp
# from match import query_details, query
from song_input import mic_input, mp3_input

import os

database.reset()
folder = "song_data"
id_count = 0
for root, dirs, files in os.walk(folder):
    for name in files:
        song_path = os.path.join(root,name)
        samples, sample_rate = mp3_input(song_path)
        log_spec, freqs, times = make_spectrogram(samples,sample_rate)
        fgp = make_fgp(find_peaks(log_spec))
        database.add(fgp, str(id_count),name[:-4])
        print("Added " + name[:-4])
        id_count = id_count + 1      