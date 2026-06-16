# Lightweight Command Line YouTube Downloader

<hr>

## Warnings

> <span style="color:#b45309"><strong>Warning:</strong></span> This project may still contain bugs. Use it carefully, especially when downloading large playlists.

> <span style="color:#b45309"><strong>Warning:</strong></span> YouTube rate limits mass downloads. Pace downloads responsibly to avoid temporary blocks, failed requests, or throttling.

> <span style="color:#b45309"><strong>Warning:</strong></span> This project is primarily based on `pytubefix`, with auxiliary features powered by `yt-dlp`. The downloader works only as long as those libraries can correctly communicate with YouTube.

<hr>

## What This Application Does

This is a lightweight command-line YouTube downloader for downloading:

- Single YouTube videos.
- YouTube Shorts, when supplied as valid video URLs.
- YouTube playlists.

The application validates user-supplied URLs, chooses the best available compatible stream up to the configured maximum resolution, downloads the media, merges separate audio/video streams when needed, checks the final file, and records download information in a JSON log.

At a high level:

1. The user chooses single-video download or playlist download.
2. The app reads download settings from `config.ini`.
3. URLs are validated and normalized where applicable.
4. `pytubefix` downloads the selected video and audio streams.
5. `ffmpeg` merges adaptive audio/video streams.
6. The merged output is checked for integrity.
7. Temporary audio/video files are removed after a successful merge.
8. A download log entry is appended to `download_log.json`.

<hr>

## System Requirements

### Required Software

| Requirement | Purpose |
| --- | --- |
| <span style="color:#2563eb"><strong>Python 3</strong></span> | Runs the application and creates the virtual environment. |
| <span style="color:#2563eb"><strong>pip</strong></span> | Installs Python dependencies from `requirements.txt`. |
| <span style="color:#2563eb"><strong>venv</strong></span> | Creates an isolated Python environment for this project. |
| <span style="color:#2563eb"><strong>FFmpeg</strong></span> | Merges adaptive video/audio streams and verifies output integrity. Must be available in `PATH`. |
| <span style="color:#2563eb"><strong>Deno</strong></span> | Required by the current dependency stack used around `yt-dlp`/EJS support. Must be available in `PATH`. |
| <span style="color:#2563eb"><strong>Internet access</strong></span> | Required for package installation, URL validation, playlist extraction, and downloads. |

### Python Libraries

The project installs its Python dependencies from `requirements.txt`. Important packages include:

- `pytubefix`: primary download engine.
- `yt-dlp`: URL validation support and playlist metadata extraction.
- `requests`, `aiohttp`, `websockets`, and related networking dependencies.
- `yt-dlp-ejs`, `nodejs-wheel-binaries`, and related support packages.

### Recommended Environment

- Windows 10/11, macOS, or Linux.
- Python 3.10 or newer is recommended.
- A stable internet connection.
- Enough disk space for downloaded video files and temporary audio/video files.

<hr>

## How To Run The App

## Windows

Windows users can use the included automated launcher:

- `WINDOWS.bat`
- `run.ps1`

`WINDOWS.bat` launches `run.ps1` with PowerShell. The PowerShell script checks for required software, prepares a virtual environment, installs dependencies, and starts `main.py`.

> <span style="color:#dc2626"><strong>Important:</strong></span> The Windows script can install software from the internet and modify user environment variables such as `PATH`. Review `run.ps1` before running it if you want to understand every change it may make.

### What The Windows Script Does

The script can:

- Detect Python from `py`, `python`, `python3`, or common install locations.
- Install Python 3.12 using `winget` if Python is missing.
- Detect FFmpeg from `PATH` or common package-manager locations.
- Install FFmpeg using `winget` if FFmpeg is missing.
- Detect Deno from `PATH` or common install locations.
- Install Deno using the official Deno install script if Deno is missing.
- Add FFmpeg and Deno folders to the current session `PATH`.
- Persist needed FFmpeg/Deno directories in the user `PATH`.
- Create a `.venv` virtual environment.
- Install packages from `requirements.txt`.
- Launch the app with `main.py`.

### Running On Windows

1. Open the project folder.
2. Double-click `WINDOWS.bat`.
3. Allow the terminal to finish installing or checking dependencies.
4. Follow the on-screen prompt:

```text
Press 1 for single video download and 2 for playlist download. Press 99 to exit program.
```

5. Paste a YouTube video URL or playlist URL when asked.

### Manual Windows Run

If you do not want to use the automated script:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Make sure `ffmpeg` and `deno` are installed and available from the same terminal:

```powershell
ffmpeg -version
deno --version
```

<hr>

## macOS And Linux

An official automated macOS/Linux setup script is still in progress. For now, macOS and Linux users should install the required utilities manually, create a virtual environment, install the Python dependencies, and run `main.py`.

### 1. Install Python

#### macOS

Using Homebrew:

```bash
brew install python
```

Check that Python is available:

```bash
python3 --version
python3 -m pip --version
```

#### Ubuntu/Debian Linux

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

Check that Python is available:

```bash
python3 --version
python3 -m pip --version
```

#### Fedora Linux

```bash
sudo dnf install python3 python3-pip
```

#### Arch Linux

```bash
sudo pacman -S python python-pip
```

### 2. Install FFmpeg

#### macOS

```bash
brew install ffmpeg
```

#### Ubuntu/Debian Linux

```bash
sudo apt update
sudo apt install ffmpeg
```

#### Fedora Linux

```bash
sudo dnf install ffmpeg
```

#### Arch Linux

```bash
sudo pacman -S ffmpeg
```

Verify that FFmpeg is available:

```bash
ffmpeg -version
```

If this command fails, add FFmpeg to your shell `PATH` before running the downloader.

### 3. Install Deno

#### macOS

Using Homebrew:

```bash
brew install deno
```

Or using the official install script:

```bash
curl -fsSL https://deno.land/install.sh | sh
```

#### Linux

```bash
curl -fsSL https://deno.land/install.sh | sh
```

After installing with the script, add Deno to your shell `PATH` if the installer asks you to. Commonly this means adding the following to `~/.zshrc`, `~/.bashrc`, or your shell config:

```bash
export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"
```

Reload your shell configuration:

```bash
source ~/.zshrc
```

or:

```bash
source ~/.bashrc
```

Verify Deno:

```bash
deno --version
```

### 4. Create A Virtual Environment

From the project folder:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

When the environment is active, your shell prompt usually shows `(.venv)`.

### 5. Install Python Dependencies

Upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

Install project dependencies:

```bash
python -m pip install -r requirements.txt
```

### 6. Run The App

```bash
python main.py
```

Then choose:

```text
1  Single video download
2  Playlist download
99 Exit
```

<hr>

## Features

### Single Video Download

- Accepts a YouTube video URL from the command line.
- Validates the URL before attempting download.
- Supports common YouTube URL formats, including:
  - `youtube.com/watch?v=...`
  - `youtu.be/...`
  - `youtube.com/shorts/...`
  - `youtube.com/embed/...`
  - `youtube.com/live/...`
- Downloads the best compatible stream at or below the configured maximum resolution.

### Playlist Download

- Accepts a YouTube playlist URL.
- Uses `yt-dlp` to extract playlist metadata and video URLs.
- Downloads each playlist video one by one.
- Continues to the next video if one video fails.
- Stores playlist downloads inside a folder named after the playlist title.

Example:

```text
Configured output folder/
└── Playlist Name/
    ├── Video One-2026-06-16_12-00-00.mp4
    └── Video Two-2026-06-16_12-05-00.mp4
```

### URL Validation And Normalization

- Single-video URLs are parsed and checked for valid YouTube video IDs.
- Playlist URLs are parsed and checked for valid playlist IDs.
- Playlist URLs are normalized to:

```text
https://www.youtube.com/playlist?list=PLAYLIST_ID
```

- Single-video validation also asks `yt-dlp` to inspect the URL before download.

### Stream Selection

- The downloader prefers `avc1` video streams for broad compatibility.
- The downloader prefers `mp4a` audio streams for compatibility with MP4 output.
- It selects the highest resolution and FPS combination at or below the configured max resolution.
- For adaptive streams, audio and video are downloaded separately and merged with FFmpeg.
- For progressive streams, the combined video/audio file is downloaded directly.

### File Integrity Checks

- Downloaded video/audio files are checked to ensure they exist and are not empty.
- Merged output files are checked with FFmpeg.
- Temporary video and audio files are removed only after the final merged file passes integrity checks.

### Logging

- Download attempts are logged to `download_log.json`.
- If the log file does not exist, the app creates it.
- If the log file is empty, invalid, or not a JSON list, the app repairs it.
- Invalid existing logs are renamed to `download_log_error_TIMESTAMP.json` before a new log file is created.

### Configuration

Download behavior can be adjusted in `config.ini`.

Current configuration:

```ini
[download]
output_path = /Users/anindyachakravarty/Desktop
max_resolution = 1080
delete_temp_files = yes
needs_login = no

[video]
preferred_codec = avc1

[audio]
preferred_codec = mp4a
```

Currently active settings:

- `output_path`: folder where downloaded files are saved.
- `max_resolution`: maximum allowed video resolution.

Present but not fully wired into the current downloader behavior:

- `delete_temp_files`
- `needs_login`
- `[video] preferred_codec`
- `[audio] preferred_codec`

<hr>

## Module Guide

### `main.py`

`main.py` is the application entry point.

It:

- Reads `max_resolution` and `output_path` from `config.ini`.
- Shows the command-line menu.
- Routes option `1` to single-video download.
- Routes option `2` to playlist download.
- Routes option `99` to program exit.
- Passes validated user choices to the downloader.

For single videos, it asks for a URL, validates it, prints the chosen settings, and calls `downloader.download()`.

For playlists, it asks for a playlist URL, fetches the playlist title, creates an output folder using that title, extracts video URLs, and downloads each video in sequence.

### `downloader.py`

`downloader.py` contains the main download logic.

It:

- Creates the output folder if it does not exist.
- Sanitizes video titles so they can safely be used as filenames.
- Uses `pytubefix.YouTube` to inspect available streams.
- Filters video streams to compatible `avc1` streams.
- Filters audio streams to compatible `mp4a` streams.
- Chooses the best video stream by resolution and FPS.
- Chooses the best audio stream by bitrate.
- Downloads progressive streams directly.
- Downloads adaptive video and audio streams separately.
- Uses FFmpeg to merge adaptive streams into a final `.mp4`.
- Uses FFmpeg to verify the final merged output.
- Deletes temporary audio/video files after successful verification.
- Sends a structured log entry to `logger.py`.

Important helper functions:

- `get_output_path()`: resolves and creates the output directory.
- `sanitize_filename()`: removes invalid filename characters and trims unsafe names.
- `get_top_video_stream()`: selects the best compatible video stream.
- `get_top_audio_stream()`: selects the best compatible audio stream.
- `merge_audio_video()`: merges separate video and audio files with FFmpeg.
- `check_video_integrity()`: checks the final media file using FFmpeg.
- `is_valid_file()`: ensures a file exists, is a file, and is not empty.

### `playlist.py`

`playlist.py` handles playlist extraction.

It:

- Validates and normalizes playlist URLs through `url_validation.py`.
- Uses `yt-dlp` in flat extraction mode.
- Extracts playlist entries without downloading them.
- Converts playlist entries into normal YouTube video URLs.
- Returns the playlist title for folder naming.

If playlist extraction fails, the module returns `None` or an empty list depending on where the failure occurs.

### `url_validation.py`

`url_validation.py` validates and normalizes YouTube URLs.

For single videos, it:

- Accepts common YouTube hostnames.
- Extracts video IDs from supported URL patterns.
- Checks that video IDs are 11 characters and contain valid YouTube ID characters.
- Normalizes valid video URLs to:

```text
https://www.youtube.com/watch?v=VIDEO_ID
```

- Uses `yt-dlp` to confirm that the normalized video URL can be inspected.

For playlists, it:

- Extracts the `list` query parameter.
- Checks that the playlist ID contains valid characters.
- Normalizes playlist URLs to:

```text
https://www.youtube.com/playlist?list=PLAYLIST_ID
```

### `logger.py`

`logger.py` manages structured download logs.

It:

- Defines a `Log` dataclass for download metadata.
- Converts log objects into dictionaries.
- Writes log entries to `download_log.json`.
- Verifies that the log file exists, is readable, contains valid JSON, and has a list as its root element.
- Creates a new empty log file when needed.
- Renames broken log files before recreating them.

Logged fields include:

- Start time and end time.
- Source URL.
- Requested resolution.
- Output path.
- Temporary video/audio filenames and paths.
- Preferred codecs used by the current downloader logic.
- Final filename and path.
- Success status.

### `run.ps1`

`run.ps1` is the Windows automation script.

It:

- Detects or installs Python.
- Detects or installs FFmpeg.
- Detects or installs Deno.
- Updates session and user `PATH` values where needed.
- Creates `.venv`.
- Installs dependencies.
- Checks that core project files exist.
- Runs `main.py`.

### `WINDOWS.bat`

`WINDOWS.bat` is a convenience launcher for Windows users.

It:

- Moves into the project folder.
- Verifies that `run.ps1` exists.
- Starts PowerShell with execution-policy bypass for this script run.
- Reports non-zero exit codes from the launcher.

### `config.ini`

`config.ini` stores user-editable settings.

Most users will primarily edit:

- `output_path`
- `max_resolution`

### `requirements.txt`

`requirements.txt` pins the Python dependencies needed by the project. Install it inside a virtual environment to avoid changing your global Python installation.

<hr>

## Responsible Use

Only download content you have the right to download. Respect YouTube's terms, creator rights, copyright law, and local regulations.

<hr>

## Work In Progress

Planned and ongoing work:

- macOS/Linux automated setup script.
- Ability to select different audio and video codecs.
- Ability to download entire channels.
- Proxy integration to help with large download batches.
- Support for location-blocked content where legally and technically possible.
- OAuth login support for age-restricted videos.
- Continued bug fixes.
- Eventual full migration from `pytubefix` to `yt-dlp`.
