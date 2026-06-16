import yt_dlp
import url_validation



def playlist_downloader(playlist_url):
    video_urls = []
    playlist_url = url_validation.validate_playlist(playlist_url)

    if playlist_url is None:
        return None

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "ignoreerrors": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)

    except yt_dlp.utils.DownloadError:
        return None

    except Exception:
        return None

    if not playlist_info:
        return None

    entries = playlist_info.get("entries")

    if not entries:
        return []

    for entry in entries:
        if entry is None:
            continue

        if entry.get("webpage_url"):
            video_urls.append(entry["webpage_url"])

        elif entry.get("url"):
            url = entry["url"]

            if url.startswith("http"):
                video_urls.append(url)
            else:
                video_urls.append(f"https://www.youtube.com/watch?v={url}")

        elif entry.get("id"):
            video_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")

    return video_urls

def get_playlist_title(playlist_url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "ignoreerrors": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)

    return playlist_info.get("title")

def main():
    playlist_url = str(input("Enter your YouTube Playlist URL: "))  #"https://youtube.com/playlist?list=PLEYJzj2wYB_I&si=Wrpl1Q6VIeHfux5q"
    print(get_playlist_title(playlist_url))
    print(playlist_downloader(playlist_url))


if __name__=="__main__":
    main()
