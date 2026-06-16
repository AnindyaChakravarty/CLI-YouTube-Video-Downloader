import os
import re
import shutil
import datetime
import subprocess
from pathlib import Path
from pytubefix import YouTube
from operator import itemgetter
from logger import Log, create_log
from pytubefix.cli import on_progress


def get_output_path(output_path=None):
    if output_path is not None:
        path = Path(output_path)
    else:
        try:
            path = Path(__file__).resolve().parent
        except NameError:
            path = Path.cwd()

    path.mkdir(parents=True, exist_ok=True)
    return path


def progress_callback(stream, chunk, bytes_remaining):
    total_size = stream.filesize

    if total_size is None:
        return

    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100

    print(f"\rDownloading: {percentage:.2f}%", end="", flush=True)


# CONVERT A STRING INTO A WINDOWS/LINUX/MAC SAFE FILENAME
# WE ARE USING THE VIDEO TITLE AS THE FINAL FILE NAME
# THERE COULD BE INVALID CHARACTERS IN THE TITLE OF THE YOUTUBE VIDEO
# CHARACTERS THAT ARE NOT ALLOWED TO BE USED IN FILENAMES


def sanitize_filename(filename, max_length=180):

    # Replace Windows-illegal filename characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Replace non-breaking spaces and weird whitespace
    filename = filename.replace("\xa0", " ")

    # Collapse repeated whitespace
    filename = re.sub(r"\s+", " ", filename)

    # Remove leading/trailing spaces and dots
    filename = filename.strip(" .")

    # Avoid empty filename
    if not filename:
        filename = "downloaded_video"

    # Keep filename length reasonable
    filename = filename[:max_length]

    return filename


# CONVERT RESOLUTION STRING TO INT AND STRIP 'p' FROM THE END OF STRING
# stream.resolution RETURNS A STRING WITH A 'p' AT THE END (ex "1080p").
# WE STRIP THE TRAILING 'p' AND THEN CONVERT IT INTO INTEGER
# SINCE OUTPUT IS STANDARD AND DOES NOT CHANGE, WE CAN HARDCODE IT FOR NOW.

def handle_res_string(stream):

    return int(stream.resolution.rstrip("p"))


# CHECK IF TOP STREAM'S VIDEO CODEC IS AVC1
# AVC1 IS THE MOST COMPATIBLE THEREFORE WE PROCEED WITH THAT

def is_avc1(stream):

    return stream.video_codec is not None and stream.video_codec.startswith("avc1")


# QUERY ITAG, VIDEO QUALITY AND FPS FOR EACH STREAM FROM LIST OF STREAMS
# STORE QUERIED DATA IN TUPLES, STORE TUPLES IN LIST
# ONLY VIDEOS OF 1080P OR LOWER QUALITY ARE EXPLORED.

def get_top_video_stream(list_of_streams, resolution_wanted=1080):

    sorted_res = []
    for stream in list_of_streams:
        # print(f'{stream}\n---------------------------\n')
        if stream.resolution and is_avc1(stream):
            resolution = handle_res_string(stream)
            if resolution <= resolution_wanted:
                sorted_res.append((stream.itag, resolution, stream.fps))
    

    # SORT LIST OF TUPLES CONTAINING QUERY ITAG, VIDEO QUALITY AND FPS TUPLES
    # SORT FIRST BY QUALITY AND THEN BY FPS (ex.: 1080p,60fps -> 1080p,30fps )

    sorted_streams = sorted(sorted_res, key=itemgetter(1,2), reverse=True)
    # print(sorted_streams)

    # RETURN THE BEST MATCHING STREAM
    top_stream = sorted_streams[0]

    return top_stream

# CHECK IF TOP STREAM'S AUDIO CODEC IS MP4A
# MP4A IS THE MOST COMPATIBLE WITH AVC1 VIDEO CODEC

def is_mp4a(stream):

    return stream.audio_codec is not None and stream.audio_codec.startswith("mp4a")


# SIMILAR TO handle_res_string() FUNCTION
# REMOVES THE TRAILING "kbps" TEXT FROM BITRATE ATTRIBUTE

def handle_bitrate_string(stream):

    return int(stream.abr.rstrip("kbps"))


# SIMILAR TO get_top_video_stream()
# CHECK IF STREAM IS AUDIO AND CODEC IS MP4A
# STORE ALL MATCHING STREAMS IN A LIST AND SORT THEM BY BITRATE
# RETURN THE HIGHEST BITRATE STREAM FROM THE LIST

def get_top_audio_stream(list_of_streams):
    
    sorted_abr = []
    for stream in list_of_streams:

        if stream.abr and is_mp4a(stream):
            bitrate = handle_bitrate_string(stream)
            sorted_abr.append((stream.itag, bitrate))

    sorted_audio_streams = sorted(sorted_abr, key=itemgetter(1), reverse=True)

    top_audio_stream = sorted_audio_streams[0]

    return top_audio_stream



def download(link, resolution=1080, output_path=None):

    # START TIMINIG OPERATION

    time_start = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # INITIALIZE VARIABLES

    video_filepath = None
    audio_filepath = None
    final_output_filepath = None
    video_status = False
    audio_status = False
    prog_status = False
    merge_status = False
    final_output_integrity = False
    status = False

    # IF NO OUTPUT PATH IS PASSED THEN THE CURRENT WORKING DIRECTORY IS FETCHED
    output_path = get_output_path(output_path)

    resolution = int(resolution)

    video_filename = f"video-{time_start}-.mp4"
    audio_filename = f"audio-{time_start}-.m4a"

    yt = YouTube(
    link,
    # use_oauth=True,
    # allow_oauth_cache=True,
    on_progress_callback=progress_callback
    )

    list_of_streams = yt.streams

    # GET THE TOP VIDEO STREAM BY ITAG
    top_stream = yt.streams.get_by_itag(get_top_video_stream(list_of_streams, resolution_wanted=resolution)[0])

    # GET THE VIDEO TITLE AND USE IT AS FINAL FILE NAME
    final_filename = f"{sanitize_filename(top_stream.title)}-{time_start}.mp4"
    

    # ADAPTIVE OR DASH STREAMS ARE HIGH RESOLUTION/QUALITY VIDEOS SPLIT INTO AUDIO & VIDEO
    # IN ORDER TO DOWNLOAD ADAPTIVE STREAMS WE HAVE TO MERGE THE AUDIO AND VIDEO IN POST
    # WE WILL BE USING ffmpeg TO MERGE THE CHANNELS AND THEN VERIFY THE MERGED OUTPUT

    if top_stream.is_adaptive:

        top_audio_stream = yt.streams.get_by_itag(get_top_audio_stream(list_of_streams)[0])

        video_filepath = top_stream.download(output_path=str(output_path),filename=video_filename)

        if not is_valid_file(video_filepath):
            raise RuntimeError("Video download failed or returned an invalid file.")

        print("\nVideo Downloaded Successfully...")
        video_status = True

        audio_filepath = top_audio_stream.download(output_path=str(output_path),filename=audio_filename)

        if not is_valid_file(audio_filepath):
            raise RuntimeError("Audio download failed or returned an invalid file.")

        print("\nAudio Downloaded Successfully...")
        audio_status = True

        final_output_filepath = merge_audio_video(video_filepath,audio_filepath,str(Path(output_path) / final_filename))
        merge_status = is_valid_file(final_output_filepath)

        final_output_integrity = check_video_integrity(final_output_filepath)
        if final_output_integrity:
            remove_residue_files(video_filepath, audio_filepath,final_output_integrity)

        status = video_status and audio_status and merge_status and final_output_integrity

    elif top_stream.is_progressive:
        
        final_output_filepath = top_stream.download(output_path=str(output_path),filename=final_filename)

        if not is_valid_file(final_output_filepath):
            raise RuntimeError("Video download failed or returned an invalid file.")
        
        print("\nVideo Downloaded Successfully...")
        prog_status = True
        status = prog_status


    time_end = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # LOG DETAILS AT THE END OF OPERATIONS

    log = Log(time_start, time_end, link, resolution, output_path,
        video_filename, video_filepath, "avc1",
        audio_filename, audio_filepath, "mp4a",
        final_filename, final_output_filepath,
        status)
    
    create_log(log)


def is_valid_file(file_path):
    if file_path is None:
        return False

    path = Path(file_path)

    return path.exists() and path.is_file() and path.stat().st_size > 0


def merge_audio_video(video_path, audio_path, output_path):
    ffmpeg_path = shutil.which("ffmpeg")

    if ffmpeg_path is None:
        raise FileNotFoundError("ffmpeg was not found in PATH")

    command = [
        ffmpeg_path,
        "-y",
        "-loglevel", "error",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "copy",
        output_path
    ]

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )
        print("\nFiles Merged Successfully...")

    except subprocess.CalledProcessError as error:
        print("FFmpeg merge failed.")
        print(error.stderr)
        raise

    return output_path


def check_video_integrity(file_path):

    if not os.path.exists(file_path):
        print("Integrity check failed: file does not exist.")
        return False

    if os.path.getsize(file_path) == 0:
        print("Integrity check failed: file is empty.")
        return False

    ffmpeg_path = shutil.which("ffmpeg")

    if ffmpeg_path is None:
        raise FileNotFoundError("ffmpeg was not found in PATH")

    command = [
        ffmpeg_path,
        "-v", "error",
        "-i", file_path,
        "-f", "null",
        "-"
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode == 0:
        print("Integrity check passed.")
        return True

    print("Integrity check failed.")
    print(result.stderr)
    return False


def remove_residue_files(video_filepath, audio_filepath,verified=bool):

    os.remove(video_filepath)
    os.remove(audio_filepath)
    print("Residue files successfully removed")


def main(url, output_path=None):
    download(url, output_path=output_path)


# CHECK IF OUTPUT PATH IS BEING FETCHED CORRECTLY

# print(get_output_path())
# print(type(get_output_path()))

# CHECK IF AUDIO AND VIDEO FILES ARE MERGED CORRECTLY

# video_filepath = r"C:\Users\Anindya\Desktop\Misc\Projects\YTD\video.mp4"
# audio_filepath = r"C:\Users\Anindya\Desktop\Misc\Projects\YTD\audio.m4a"
# final_output_filepath = merge_audio_video(video_filepath, audio_filepath, r"C:\Users\Anindya\Desktop\Misc\Projects\YTD\final.mp4")

# CHECK IF FILE ITEGRITY VERIFICATION IS WORKING CORRECTLY

# final_output_integrity = check_video_integrity(final_output_filepath)

# CHECK IF RESIDUE FILES ARE BEING REMOVED PROPERLY

# remove_residue_files(video_filepath, audio_filepath, final_output_integrity)

# RUN MAIN SCRIPT

if __name__=="__main__":
    url = 'https://www.youtube.com/watch?v=Q8-msNmFKN4'
    main(url)
