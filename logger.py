import json
from pathlib import Path
import datetime
import os
from dataclasses import dataclass, asdict

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "download_log.json"

@dataclass
class Log:
    time_start: str | None
    time_end: str | None
    url: str | None
    resolution: int | None
    output_path: str | None
    vfilename: str | None
    vfilepath: str | None
    vcodec: str | None
    afilename: str | None
    afilepath: str | None
    acodec: str | None
    final_filename: str | None
    final_filepath: str | None
    status: bool | None


def create_log(log: Log):
    log_data = asdict(log)
    write_to_json(log_data)
    return log_data



def verify_json(path):
    path = Path(path)

    # 0. Check if file exists
    if not path.exists():
        return {
            "status": 0,
            "valid": False,
            "message": "File does not exist",
            "data": None
        }

    # Extra safety: path exists but is not a file
    if not path.is_file():
        return {
            "status": -1,
            "valid": False,
            "message": "Path exists but is not a file",
            "data": None
        }

    # 1. Check if file is empty
    try:
        content = path.read_text(encoding="utf-8").strip()
    except Exception:
        return {
            "status": 2,
            "valid": False,
            "message": "File could not be read",
            "data": None
        }

    if content == "":
        return {
            "status": 1,
            "valid": False,
            "message": "File is empty",
            "data": None
        }

    # 2. Check if it is valid JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {
            "status": 2,
            "valid": False,
            "message": "File does not contain valid JSON",
            "data": None
        }

    # 3. Check if base element is a list
    if not isinstance(data, list):
        return {
            "status": 3,
            "valid": False,
            "message": "JSON base element is not a list",
            "data": data
        }

    # 4. Everything is okay
    return {
        "status": 4,
        "valid": True,
        "message": "File exists, contains valid JSON, and base element is a list",
        "data": data
    }


def create_empty_log_file():
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump([], file, indent=4)


def rename_bad_log_file():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    error_file = SCRIPT_DIR / f"download_log_error_{timestamp}.json"

    try:
        os.rename(LOG_FILE, error_file)
    except Exception:
        pass


def handle_json_file(verification_report=None):

    # CHECK LOG FILE INTEGRITY
    if not verification_report:
        verification_report = verify_json(LOG_FILE)

    # IF JSON IS A VALID FILE AND CORRECTLY FORMATTED
    if verification_report["status"] == 4:
        return True

    # FILE DOES NOT EXIST OR FILE IS EMPTY
    # Just create/overwrite with an empty list
    if verification_report["status"] in (0, 1):
        create_empty_log_file()

    # FILE EXISTS BUT IS BAD:
    # - path exists but is not a file
    # - bad JSON
    # - valid JSON but not a list
    elif verification_report["status"] in (-1, 2, 3):
        rename_bad_log_file()
        create_empty_log_file()

    # VERIFY AGAIN AFTER REPAIR
    verification_report = verify_json(LOG_FILE)

    if verification_report["status"] == 4:
        return True

    return False


def write_to_json(log_data):

    if handle_json_file():
        with open(LOG_FILE, "r+", encoding="utf-8") as file:
            existing_log_data = json.load(file)
            existing_log_data.append(log_data)

            file.seek(0)
            json.dump(existing_log_data, file, indent=4)
            file.truncate()

def main():

    ex ={
    "time_start": "2026-06-14_20-06-32",
    "time_end": "2026-06-14_20-06-33",
    "video_link": "https://www.youtube.com/watch?v=Eaqr79zvqIw",
    "resolution": 1080,
    "output_path": ".",
    "video_filename": "video-2026-06-14_20-06-32-.mp4",
    "video_filepath": "C:\\Users\\Anindya\\Desktop\\Misc\\Projects\\YTD\\video-2026-06-14_20-06-32-.mp4",
    "video_codec": "avc1",
    "audio_filename": "audio-2026-06-14_20-06-32-.m4a",
    "audio_filepath": "C:\\Users\\Anindya\\Desktop\\Misc\\Projects\\YTD\\audio-2026-06-14_20-06-32-.m4a",
    "audio_codec": "mp4a",
    "final_filename": "How To_ Resistance Band Squat.mp4",
    "final_filepath": ".\\How To_ Resistance Band Squat.mp4"
    }

    write_to_json(ex)




if __name__ == "__main__":
    main()
