from moviepy.editor import *
from tinytag import TinyTag
import string
import os
import time

## Used to remove extra covers for tracks downloaded from Deezer after Beets tagging
def check_folder(folder):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f))]
    for file in files:
        filename = os.path.splitext(file)[0]
        if filename.lower() == "cover.1":
            os.remove(os.path.join(folder, file))
            print("Removed : " + os.path.join(folder, file))
    subfolders = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder,f))]
    for f2 in subfolders:
        check_folder(os.path.join(folder,f2))
                 
base_folder = "D:/Music/Sorted"

check_folder(base_folder)
