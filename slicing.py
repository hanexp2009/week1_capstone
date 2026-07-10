from song_input import mp3_input
import numpy as np
import os
SLICES = 10
SLICE_TIME = 15

def split_mp3(file_path, slice_time, slices):
    samples, sample_rate = mp3_input(file_path)
    #samples is now ready to be split
    #samples size -> length * sample_rate
    target_size = int(sample_rate * slice_time)
    max_start = len(samples) - target_size
    return_arr = []

    for i in range(slices):
        start_idx = np.random.randint(0, max_start+1)
        end_idx = start_idx+target_size
        idx_arr = samples[start_idx:end_idx]
        return_arr.append(idx_arr)
    return return_arr

# file_paths = ["/Users/bagel/Documents/GitHub/week1_capstone/Week 1 - Shazam Kid/Classical Piano/Bach - Prelude & Fugue No. 2 in C Minor.mp3", "/Users/bagel/Documents/GitHub/week1_capstone/Week 1 - Shazam Kid/Country Music/Amarillo By Morning 4.mp3", "/Users/bagel/Documents/GitHub/week1_capstone/Week 1 - Shazam Kid/EdM/Animals - Martin Garrix - Official Audio HD 4.mp3", "/Users/bagel/Documents/GitHub/week1_capstone/Week 1 - Shazam Kid/Jazz/L-O-V-E.mp3", "/Users/bagel/Documents/GitHub/week1_capstone/Week 1 - Shazam Kid/Nursery/BAA BAA BLACK SHEEP Children_s Song with Lyrics 4.mp3", "/Users/bagel/Documents/GitHub/week1_capstone/Week 1 - Shazam Kid/Pop/Billie Eilish - bad guy (Audio) 4.mp3", "/Users/bagel/Documents/GitHub/week1_capstone/Week 1 - Shazam Kid/Rock/Creedence Clearwater Revival - Fortunate Son.mp3"]
# os.makedirs("/Users/bagel/Documents/GitHub/week1_capstone/tests_manual/pure_song_splits", exist_ok=True)
# for file in file_paths:
#     song_splits = split_mp3(file, SLICE_TIME, SLICES)
#     song_name = os.path.splitext(os.path.basename(file))[0]
#     np.save(f"/Users/bagel/Documents/GitHub/week1_capstone/tests_manual/pure_song_splits/{song_name}", song_splits)

