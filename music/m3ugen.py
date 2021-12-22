from moviepy.editor import *
from tinytag import TinyTag
import string
import os
import time

def isEnglish(s):
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True

def allEnglish(songs):
    english = True
    for song in songs:
        if not isEnglish(song):
            english = False
    return english


def write_playlist(folder):
    songs = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith("mp3") or f.lower().endswith("flac")]
    if (len(songs) > 2):
        current_m3u = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith("m3u") or f.lower().endswith("m3u8")]
        if len(current_m3u)> 0:
            for playlist in current_m3u:
                 os.remove(os.path.join(folder, playlist))
        first_song_tag = TinyTag.get(os.path.join(folder,songs[0]))
        album = "folder" if first_song_tag.album is None else first_song_tag.album
        disc = first_song_tag.disc
        disc = 1 if disc is None else int(disc)
        album = album.translate(str.maketrans(string.punctuation, "_"*len(string.punctuation)))
        if disc > 1 :
             album = album + " - Disc " + first_song_tag.disc
        extension = ".m3u" if allEnglish(songs) else ".m3u8"
        print(extension)
        f = open(os.path.join(folder, album + extension), "w", encoding='utf-8')
        f.write("\n".join(songs))
        f.close()
        print("playlist generated for " + album)
    else:
        print("skipped " + folder)

def check_folder(folder):
    write_playlist(folder)
    subfolders = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder,f))]
    for f2 in subfolders:
        check_folder(os.path.join(folder,f2))
                 
base_folder = "D:/Music/Sorted"

check_folder(base_folder)
