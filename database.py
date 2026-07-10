"""
Load and add items to the database, db.pkl
"""

import pickle
from typing import List,Tuple

def load() -> dict:
    try:
        with open("db.pkl", mode = "rb") as opened_file:
            return pickle.load(opened_file)
    except EOFError:
        a = {}
        return a

def loadSongs() -> dict:
    try:
        with open("songs.pkl", mode = "rb") as opened_file:
            return pickle.load(opened_file)
    except EOFError:
        a = {}
        return a

def export(d: dict):   
    with open("db.pkl",mode="wb") as opened_file:
        pickle.dump(d,opened_file)

def exportSongs(d: dict):   
    with open("songs.pkl",mode="wb") as opened_file:
        pickle.dump(d,opened_file)

def add(fanout: List[Tuple[Tuple[float,float,float],float]], song_ID: str, song_name: str):
    d = load()
    for pair in fanout:
        if pair[0] not in d:
            d[pair[0]] = []
        d[pair[0]].append((song_ID, pair[1]))
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
    songs.pop(songID,None)
    exportSongs(songs)

def view():
    print(load())

def viewSongs():
    print(loadSongs())

def reset():
    a = {}
    export(a)
    exportSongs(a)

def query(fingerprints: List[Tuple[Tuple[float,float,float],float]]):
    counts = {}
    database = load()
    for fp in fingerprints:
        time_clip = fp[1]
        for match in [key for key in database if key == fp[0]]:
            for id,time in database[match]:
                if (id, time_clip - time) not in counts:
                    counts[(id, time_clip - time)] = 1
                else:
                    counts[(id, time_clip - time)] += 1
    song_data = loadSongs()
    best_match = song_data[max(counts,key=counts.get)[0]]
    return best_match
