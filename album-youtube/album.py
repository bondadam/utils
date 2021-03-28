from moviepy.editor import *
from pathlib import Path
from tinytag import TinyTag
import argparse
import os
import time


def first(iterable, condition = lambda x: True):
    """
    Returns the first item in the `iterable` that
    satisfies the `condition`.

    If the condition is not given, returns the first item of
    the iterable.

    Raises `StopIteration` if no item satysfing the condition is found.

    >>> first( (1,2,3), condition=lambda x: x % 2 == 0)
    2
    >>> first(range(3, 100))
    3
    >>> first( () )
    Traceback (most recent call last):
    ...
    StopIteration
    """

    return next(x for x in iterable if condition(x))

parser = argparse.ArgumentParser(description='Make videos of songs/albums with timestamps and album cover for youtube!')
parser.add_argument("--source", default = os.getcwd(), help="Source directory where the program should look for audio files and images.")
parser.add_argument("--destination", default = os.environ["HOMEPATH"], help="Path to save video in.")
parser.add_argument("--filename", help="Video filename.")

args = parser.parse_args()
args.source = input("Absolute adress of folder?:\n")


files = [f for f in os.listdir(args.source) if os.path.isfile(os.path.join(args.source, f))]

cover_files = [f for f in files if f.lower().endswith(".png") or f.lower().endswith(".jpg") or f.lower().endswith(".jpeg") or f.lower().endswith(".gif")]

for image in cover_files:
    minus_extension = Path(os.path.join(args.source, image)).stem
    if (minus_extension.lower() in ["front", "cover", "folder"]):
        cover_files.insert(0, cover_files.pop(cover_files.index(image)))
print(cover_files[0])


description = ""

song_files = [f for f in files if f.endswith(".mp3") or f.endswith(".flac")]

first_song_tag = TinyTag.get(os.path.join(args.source,song_files[0]))
artist = first_song_tag.artist
album = first_song_tag.album
year = first_song_tag.year

description += "{0} - {1} \n{2}\n\n".format(artist,album,year)

song_names = [TinyTag.get(os.path.join(args.source,song)).title for song in song_files]

audio_clips = [AudioFileClip(os.path.join(args.source,song)) for song in song_files]

current_time = 0
track_list = song_names[:]
for i in range(len(track_list)):
    track_list[i] += " " + time.strftime('%M:%S', time.gmtime(current_time))
    audio_clips[i] = audio_clips[i].set_start(current_time)
    current_time += audio_clips[i].duration

description += "\n".join(track_list)

final_audio = CompositeAudioClip(audio_clips)
print(final_audio.duration)

if len(cover_files) == 1:
    image_clip = ImageClip(os.path.join(args.source, cover_files[0]))
    image_clip.duration=current_time
    final_slideshow = image_clip
else:
    image_clips = []
    current_image = 0
    image_time = 0
    while image_time < current_time:
        new_image_clip = ImageClip(os.path.join(args.source, cover_files[current_image]))
        if image_time + 30 > current_time:
            new_image_clip.duration= current_time - image_time
        else:
            new_image_clip.duration=30
        image_clips.append(new_image_clip)
        image_time = image_time + 30
        current_image = (current_image + 1) % len(cover_files)
    final_slideshow = concatenate(image_clips, method="compose")

    
final_clip = final_slideshow.set_audio(final_audio)
final_clip = final_clip.resize(width=1280)

if args.filename is None:
    if len(song_files) == 1:
        args.filename = first_song_tag.title + ".mp4"
    else:
        args.filename = album + ".mp4"

print(args.filename)


final_clip.write_videofile(os.path.join(args.destination, args.filename), fps=10, audio_fps=44100, audio_bitrate="320k", bitrate="2000k")

file = open(os.path.join(args.destination, album + "_description.txt"),"w") 
file.write(description)
file.close() 

###write_videofile(self, filename, fps=None, codec=None, bitrate=None, audio=True, audio_fps=44100, preset='medium', audio_nbytes=4, audio_codec=None, audio_bitrate=None, audio_bufsize=2000, temp_audiofile=None, rewrite_audio=True, remove_temp=True, write_logfile=False, verbose=True, threads=None, ffmpeg_params=None, logger='bar')
