from collections import Counter

from database import load, loadSongs


def query(fingerprints: list[tuple[tuple[int, int, int], int]]):
    counts = Counter()
    database = load()

    for fp in fingerprints:
        key, time_clip = fp

        for song_ID, time_song in database.get(key, []):
            offset = time_clip - time_song
            counts[(song_ID, offset)] += 1

    if not counts:
        return None

    songs = loadSongs()
    best_song_ID, best_offset = max(counts, key=counts.get)

    return songs.get(best_song_ID, best_song_ID)


def query_details(fingerprints: list[tuple[tuple[int, int, int], int]]):
    counts = Counter()
    database = load()

    for fp in fingerprints:
        key, time_clip = fp

        for song_ID, time_song in database.get(key, []):
            offset = time_clip - time_song
            counts[(song_ID, offset)] += 1

    if not counts:
        return None, 0, counts

    best_song_ID, best_offset = max(counts, key=counts.get)
    best_count = counts[(best_song_ID, best_offset)]

    songs = loadSongs()
    best_song_name = songs.get(best_song_ID, best_song_ID)

    return best_song_name, best_count, counts