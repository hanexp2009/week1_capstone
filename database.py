"""
Tasks:
- master method that imports an mp3 file
    - sampling the file + converting it into a spectrogram
    - create fingerprints
    - add to database dictionary
"""

import pickle

def load() -> dict:
    with open("db.pkl", mode = "rb") as opened_file:
        return pickle.load(opened_file)

def export(d: dict):   
    with open("db.pkl",mode="wb") as opened_file:
        pickle.dump(d,opened_file)

def add(fanout: list[tuple[tuple[float,float,float],float]], song: str):
    d = load()
    for pair in fanout:
        if pair[0] not in d:
            d[pair[0]] = []
        d[pair[0]].append((song, pair[1]))
    export(d)


