from tinytag import TinyTag
from pathlib import Path
from typing import List
from dataclasses import dataclass
import argparse
import os
import time
import random
import string

@dataclass
class Song:
    title: str
    artist: str
    duration: int

@dataclass
class Album:
    title: str
    artist: str
    year: int
    songs : List[Song]

    def get_length_in_milliseconds(self) -> int:
        total = 0
        for song in self.songs:
            total += song.duration
        return total

DEFAULT_IMAGE_DURATION = 30

image_formats = ["png", "gif", "jpg", "jpeg", "bmp"]
song_formats  = ["mp3", "m4a", "ogg", "flac", "aac"]


def make_album(source_dir, song_files):
    all_song_tags = [
        TinyTag.get(os.path.join(source_dir, song)) for song in song_files
    ]
    
    ## if the album is properly tagged,
    ## albumartist contains Various Artists
    ## in case of a compilation
    
    all_songs = [Song(song_tags.title, song_tags.artist, song_tags.duration) for song_tags in all_song_tags]
    album = Album(all_song_tags[0].album, all_song_tags[0].albumartist, all_song_tags[0].year, all_songs)
    return album

def random_string(chars = string.ascii_letters + string.digits, string_length=10):
	return ''.join(random.choice(chars) for i in range(string_length))
    
    

def make_description(album):
    description = ""
    description += "{0} - {1} \n{2}\n\n".format(album.artist, album.title, album.year)
    
    current_time = 0
    col_width = max(len(f"{song.artist} – {song.title}") for song in album.songs) + 2  # padding
    song_descriptions = []
    for song in album.songs:
        song_descriptions.append("".join(desc_part.ljust(col_width) for desc_part in [f"{song.artist} – {song.title}", f"{time.strftime('%M:%S', time.gmtime(current_time))}"]))
        current_time += song.duration
    
    description += "\n".join(song_descriptions)
    return description

def sanitize_ffmpeg(file_string):
    return file_string.replace("'", "'\''")

def make_songs_file_content(source_dir, song_files):
    song_file_lines = [f"file '{sanitize_ffmpeg(os.path.join(source_dir, song_file_path))}'" for song_file_path in song_files]
    song_file_lines.append("# This temporary file was generated with youtube-album.py to be used with ffmpeg.")
    return song_file_lines
    
def make_images_file_content(source_dir, cover_files, image_duration, album_duration):
    current_duration = 0
    image_file_lines = []
    while current_duration < album_duration:
        for cover_file_path in cover_files:
            image_file_lines.append(f"file '{sanitize_ffmpeg(os.path.join(source_dir, cover_file_path))}'")
            image_file_lines.append(f"duration {image_duration}")
            current_duration += image_duration
    image_file_lines.append("# This temporary file was generated with youtube-album.py to be used with ffmpeg.")
    return image_file_lines


def main(args):
    all_files = [
        f
        for f in os.listdir(args.source)
        if os.path.isfile(os.path.join(args.source, f))
    ]

    # Filter images from files
    cover_files = [f for f in all_files if f.lower().split(".")[-1] in image_formats]

    # If we find an image called front, cover or folder, make sure it comes first
    for image in cover_files:
        minus_extension = Path(os.path.join(args.source, image)).stem
        if minus_extension.lower() in ["front", "cover", "folder"]:
            cover_files.insert(0, cover_files.pop(cover_files.index(image)))

    # Filter songs from files
    song_files = [f for f in all_files if f.lower().split(".")[-1] in song_formats]
    
    album = make_album(args.source, song_files)
    description = make_description(album)
    
    description_file_path = os.path.join(args.destination, f"{album.artist} - {album.title} - description.txt")
    with open(description_file_path, "w", encoding="utf-8") as file:
        file.write(description)
        print(f"Description file written at {description_file_path}")
        file.close()
    
    songs_file_path = f"_temp_songs_{random_string()}.txt"
    with open(songs_file_path, 'w') as songs_file:
        songs_file.write("\n".join(make_songs_file_content(args.source, song_files)))

    images_file_path = f"_temp_images_{random_string()}.txt"
    with open(images_file_path, 'w') as images_file:
        images_file.write("\n".join(make_images_file_content(args.source, cover_files, DEFAULT_IMAGE_DURATION, album.get_length_in_milliseconds())))
        
    if not args.onlydesc:
        audio_clips = [
            AudioFileClip(os.path.join(args.source, song)) for song in song_files
        ]
        current_time = 0
        for i in range(len(album.songs)):
            audio_clips[i] = audio_clips[i].set_start(current_time)
            current_time += audio_clips[i].duration
        final_audio = CompositeAudioClip(audio_clips)

        if len(cover_files) == 1:
            image_clip = ImageClip(os.path.join(args.source, cover_files[0]))
            image_clip.duration = current_time
            final_slideshow = image_clip
        else:
            image_clips = []
            current_image = 0
            image_time = 0
            while image_time < current_time:
                new_image_clip = ImageClip(
                    os.path.join(args.source, cover_files[current_image])
                )
                if image_time + 30 > current_time:
                    new_image_clip.duration = current_time - image_time
                else:
                    new_image_clip.duration = 30
                image_clips.append(new_image_clip)
                image_time = image_time + 30
                current_image = (current_image + 1) % len(cover_files)
                print(cover_files[current_image])
                print(image_time)
            final_slideshow = concatenate(image_clips, method="compose")

        final_clip = final_slideshow.set_audio(final_audio)
        final_clip = final_clip.resize(width=1280)

        if args.filename is None:
            if len(song_files) == 1:
                final_filename = f"{album.songs[0].title}.mp4"
            else:
                final_filename = f"{album.artist} - {album.title}.mp4"
        else:
            final_filename = args.filename

        final_clip.write_videofile(
            os.path.join(args.destination, final_filename),
            fps=10,
            audio_fps=44100,
            audio_bitrate="320k",
            bitrate="2000k",
            threads = 6,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Make videos of songs/albums with timestamps and album cover for youtube!"
    )
    parser.add_argument(
        "source",
        metavar="directory",
        type=str,
        help="Target directory where the program should look for audio files and images.",
    )
    parser.add_argument(
        "--destination", default=os.environ["HOMEPATH"], help="Path to save video in."
    )
    parser.add_argument("--filename", help="Video filename.")
    parser.add_argument(
        "--onlydesc",
        help="Only generate description file, skip any actual video/audio editing.",
        action="store_true",
    )

    args = parser.parse_args()
    main(args)
