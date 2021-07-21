# utils
Various quick and useful scripts.


### mal3x3

Generate 3x3 collage of your favorite anime/manga on myanimelist.com

Worked with the old version of the site, needs to be updated to work with the redesign.


### album-youtube

Generate video from flac/mp3 files in given folder using pictures in the folder for a slideshow. Generates text file with start time of every song.
Perfect for quickly uploading full albums to youtube.

Unstable at the moment as I'm in the process of moving the backend from relying on moviepy to ffmpeg which should result in a nice performance boost.

Dependencies: moviepy, pathlib, tinytag