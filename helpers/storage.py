# helpers/storage.py
import os
import shutil
from uuid import uuid4

DYNAMIC_PATH = None

def init_storage(config):
    global DYNAMIC_PATH
    DYNAMIC_PATH = config.get("dynamic-storage-path", "./dynamic_charts")
    os.makedirs(DYNAMIC_PATH, exist_ok=True)

def save_chart_file(filename: str, content: bytes):
    # create unique id directory for each song
    uid = uuid4().hex
    song_dir = os.path.join(DYNAMIC_PATH, uid)
    os.makedirs(song_dir, exist_ok=True)
    filepath = os.path.join(song_dir, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    return uid, filepath

def remove_song_dir(uid: str):
    p = os.path.join(DYNAMIC_PATH, uid)
    if os.path.exists(p):
        shutil.rmtree(p)
