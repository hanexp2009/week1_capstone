"""
Load and add items to the database, db.pkl
"""

import pickle

def load() -> dict:
    try:
        with open("db.pkl", mode = "rb") as opened_file:
            return pickle.load(opened_file)
    except EOFError:
        a = {}
        return a

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

def remove(song: str):
    d = load()
    for key in d:
        d[key] = [pair for pair in d[key] if pair[0] != song]
    export(d)


def view():
    print(load())

def reset():
    a = {}
    export(a)

