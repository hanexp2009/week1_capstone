"""Load and add items to the database."""

import pickle
from typing import List,Tuple

DB_PATH = "db.pkl"
SONGS_PATH = "songs.pkl"


def load() -> dict:
    try:
        with open(DB_PATH, mode="rb") as opened_file:
            return pickle.load(opened_file)
    except (FileNotFoundError, EOFError):
        return {}


def loadSongs() -> dict:
    try:
        with open(SONGS_PATH, mode="rb") as opened_file:
            return pickle.load(opened_file)
    except (FileNotFoundError, EOFError):
        return {}


def export(d: dict):
    with open(DB_PATH, mode="wb") as opened_file:
        pickle.dump(d, opened_file)


def exportSongs(d: dict):
    with open(SONGS_PATH, mode="wb") as opened_file:
        pickle.dump(d, opened_file)


def add(fanout: List[Tuple[Tuple[int, int, int], int]], song_ID: str, song_name: str):
    d = load()

    for pair in fanout:
        key, t_anchor = pair

        if key not in d:
            d[key] = []

        d[key].append((song_ID, t_anchor))

    export(d)

    songs = loadSongs()
    songs[song_ID] = song_name
    exportSongs(songs)


def remove(songID: str):
    d = load()

    for key in d:
        d[key] = [pair for pair in d[key] if pair[0] != songID]

    export(d)

    songs = loadSongs()
    songs.pop(songID, None)
    exportSongs(songs)


def view():
    print(load())


def viewSongs():
    print(loadSongs())


def reset():
    export({})
    exportSongs({})
