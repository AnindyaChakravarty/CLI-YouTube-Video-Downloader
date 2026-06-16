import downloader
import configparser
import playlist
import url_validation
from pathlib import Path

def get_config():
    config = configparser.ConfigParser()
    config.read("config.ini")

    resolution = config["download"]["max_resolution"]
    output_path = config["download"]["output_path"]

    return resolution, output_path


def single_download(resolution, output_path):
    url = str(input("Paste your YouTube Video URL here: ")) #https://www.youtube.com/watch?v=Q8-msNmFKN4
    if not url:
        print("No URL provided.")
        return False

    print(
        f"Your URL: {url}\n"
        f"Your Download Location: {output_path}\n"
        f"Your Chosen Resolution: {resolution}"
    )
    if not url_validation.validate_single(url):
        return None
    print("Starting Script Now...")
    try:
        downloader.download(
            url,
            resolution=resolution,
            output_path=output_path
        )

    except Exception as error:
        print("Download failed.")
        print(f"Reason: {error}")
        return False
    
    print("Download completed successfully.")
    return True

def playlist_download(resolution, output_path):
    playlist_url = str(input("Paste your YouTube Playlist URL here: ")) #"https://youtube.com/playlist?list=PLEYJzj2wYB_I&si=Wrpl1Q6VIeHfux5q"
    playlist_title = playlist.get_playlist_title(playlist_url)
    output_path = str(Path(output_path) / playlist_title)
    print(f"Your URL: {playlist_url}\nYour Download Location: {output_path}\nYour Chosen Resolution: {resolution}\nStarting Script Now...")
    url_list = playlist.playlist_downloader(playlist_url)
    for url in url_list:
        try:
            downloader.download(url, resolution=resolution, output_path=output_path)
        except Exception as error:
            print(f"Failed to Download video - {url}")
            print(error)
            continue


def main(state=bool):
    running = state

    config = get_config()
    resolution = config[0]
    output_path = config[1]

    while running:
        print("Press 1 for single video download and 2 for playlist download. Press 99 to exit program.")
        operation = int(input("Enter your choice: "))
        if operation == 1:
            single_download(resolution, output_path)
        elif operation == 2:
            playlist_download(resolution, output_path)
        elif operation == 99:
            running = False
        else:
            print("Wrong choice, please press either 1,2 or 99")


if __name__ == "__main__":
    main(True)
