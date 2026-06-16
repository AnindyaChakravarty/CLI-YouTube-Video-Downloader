from urllib.parse import urlparse, parse_qs
import yt_dlp




############################################################
# SINGLE VIDEO URL VALIDATION
############################################################

def extract_youtube_video_id(url: str) -> str | None:

    YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtu.be",
    }

    if not url or not isinstance(url, str):
        return None

    url = url.strip()
    parsed = urlparse(url)

    host = parsed.netloc.lower()

    if host not in YOUTUBE_HOSTS:
        return None

    # Case 1: https://youtu.be/VIDEO_ID
    if host in {"youtu.be", "www.youtu.be"}:
        video_id = parsed.path.strip("/").split("/")[0]
        return video_id if is_valid_youtube_id(video_id) else None

    # Case 2: https://www.youtube.com/watch?v=VIDEO_ID
    if parsed.path == "/watch":
        query = parse_qs(parsed.query)
        video_id = query.get("v", [None])[0]
        return video_id if is_valid_youtube_id(video_id) else None

    # Case 3: https://www.youtube.com/shorts/VIDEO_ID
    if parsed.path.startswith("/shorts/"):
        video_id = parsed.path.split("/shorts/")[1].split("/")[0]
        return video_id if is_valid_youtube_id(video_id) else None

    # Case 4: https://www.youtube.com/embed/VIDEO_ID
    if parsed.path.startswith("/embed/"):
        video_id = parsed.path.split("/embed/")[1].split("/")[0]
        return video_id if is_valid_youtube_id(video_id) else None

    # Case 5: https://www.youtube.com/live/VIDEO_ID
    if parsed.path.startswith("/live/"):
        video_id = parsed.path.split("/live/")[1].split("/")[0]
        return video_id if is_valid_youtube_id(video_id) else None

    return None


def is_valid_youtube_id(video_id: str | None) -> bool:
    """
    YouTube video IDs are commonly 11 characters using:
    letters, numbers, underscore, and hyphen.
    """

    if not video_id:
        return False

    if len(video_id) != 11:
        return False

    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"

    return all(char in allowed_chars for char in video_id)


def normalize_youtube_url(url: str) -> str | None:
    """
    Converts a valid YouTube video URL into one standard format.
    """

    video_id = extract_youtube_video_id(url)

    if not video_id:
        return None

    return f"https://www.youtube.com/watch?v={video_id}"


def check_video_with_ytdlp(url: str) -> dict | None:
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info

    except Exception:
        return None


def validate_single(url):
    normalized_url = normalize_youtube_url(url)

    if normalized_url is None:
        print("Invalid YouTube video URL.")
        return False
    else:
        video_info = check_video_with_ytdlp(normalized_url)

        if video_info is None:
            print("Invalid YouTube video URL.")
            return False

        else:
            print("Video is valid...")
            return True
        

############################################################
# PLAYLIST URL VALIDATION
############################################################

def is_valid_youtube_playlist_id(playlist_id: str | None) -> bool:

    if not playlist_id:
        return False

    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"

    return all(char in allowed_chars for char in playlist_id)


def extract_youtube_playlist_id(url: str) -> str | None:
    """
    Extracts a YouTube playlist ID from common YouTube playlist URL formats.

    Returns:
        playlist_id if the URL looks like a valid YouTube playlist URL.
        None otherwise.
    """

    YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtu.be",
    }

    if not url or not isinstance(url, str):
        return None

    url = url.strip()
    parsed = urlparse(url)

    host = parsed.netloc.lower()

    if host not in YOUTUBE_HOSTS:
        return None

    query = parse_qs(parsed.query)

    playlist_id = query.get("list", [None])[0]

    if is_valid_youtube_playlist_id(playlist_id):
        return playlist_id

    return None


def is_youtube_playlist_url(url: str) -> bool:
    """
    Checks whether the supplied URL looks like a YouTube playlist URL.
    """

    return extract_youtube_playlist_id(url) is not None


def normalize_youtube_playlist_url(url: str) -> str | None:
    """
    Converts a valid-looking YouTube playlist URL into a standard playlist URL.

    Example:
        https://www.youtube.com/watch?v=abc123&list=PLxyz

    Becomes:
        https://www.youtube.com/playlist?list=PLxyz
    """

    playlist_id = extract_youtube_playlist_id(url)

    if not playlist_id:
        return None

    return f"https://www.youtube.com/playlist?list={playlist_id}"


def validate_playlist(url):

    normalized_playlist_url = normalize_youtube_playlist_url(url)

    if normalized_playlist_url is None:
        print("Invalid YouTube playlist URL.")
        return None
    else:
        print(f"Valid Playlist URL: {url}")
        print(f"URL Normalized to {normalized_playlist_url}")
        return normalized_playlist_url   

def main(state):
    running = state
    while running:
        print("Press 1 for single video URL Validation and 2 for playlist URL Validation. Press 99 to exit program.")
        operation = int(input("Enter your choice: "))
        if operation == 1:
            url = str(input("Enter Single Video URL: "))
            validate_single(url)
        elif operation == 2:
            url = str(input("Enter Playlist URL: "))
            validate_playlist(url)
        elif operation == 99:
            running = False
        else:
            print("Wrong choice, please press either 1,2 or 99")


if __name__=="__main__":
    main(True)
    # https://www.youtube.com/watch?v=Q8-msNmFKN4
            