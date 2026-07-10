import numpy as np
from scipy.ndimage import maximum_filter


def find_peaks(log_spec, percentile=75, neighborhood_size=20):
    cutoff = np.percentile(log_spec, percentile)

    local_max = log_spec == maximum_filter(log_spec, size=neighborhood_size)
    strong = log_spec > cutoff

    peaks = np.argwhere(local_max & strong)
    return peaks


def make_fgp(peaks, fanout=15, max_dt=None):
    peaks = sorted(map(tuple, peaks), key=lambda x: (x[1], x[0]))
    fingerprints = []

    for i, (f1, t1) in enumerate(peaks):
        count = 0

        for f2, t2 in peaks[i + 1:]:
            dt = t2 - t1

            if dt <= 0:
                continue

            if max_dt is not None and dt > max_dt:
                break

            fingerprints.append(((int(f1), int(f2), int(dt)), int(t1)))

            count += 1
            if count >= fanout:
                break

    return fingerprints