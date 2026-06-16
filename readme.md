# LIGHTWEIGHT COMMAND LINE YOUTUBE VIDEO DOWNLOADER

What it does:

When supplied with a link:

1.  Verify the link
2.  Check for all the videos at and below the set quality. So that if the set quality is not available then the next best quality video is downloaded.
3.  Checks if the selected stream is adaptive or progressive. 
4.  If stream is adaptive then it will also check for the highest quality compatible audio stream.
    1.  Download both audio and video streams 
    2.  Merge both channels using FFMPEG
    3.  Verify merged file integrity
    4.  Remove audio and video residue files 
5.  If stream is progressive, it will download the video and check its integrity.
6.  If downloads are successful then a log is created and stored inside a JSON file. With consequent downloads logs are appended to this JSON file.
7.  If supplied link is a playlist, steps 1 to 6 is repeated for each video in the said playlist.
8.  Playlist is save in a folder named after the playlist name.

&nbsp;

Can Download:

Single Video/Short

Playlist

&nbsp;

Future Features:

MacOS/Linux Automated Script to download and install all necessary software and run application.

Allow selection of different audio and video codecs