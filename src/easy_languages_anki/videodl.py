import configparser
import youtube_dl
from pathlib import Path


def download_youtube(youtube_id: str, out_dir: Path) -> tuple[Path, Path]:
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    filename = youtube_id

    ydl_opts = {
        "format": "best",
        "outtmpl": str(out_dir / f"{filename}.%(ext)s"),
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if not info:
            raise ValueError("`youtube-dl` returned no info")
        video_title = info.get("title")
        ext = info.get("ext")

    config = configparser.ConfigParser()
    config["video"] = {
        "url": url,
        "id": youtube_id,
    }

    if video_title and type(video_title) is str:
        config["video"]["title"] = video_title
    elif video_title:
        print(f"[warn] `video_title` is not a string: {video_title}")
    else:
        print("[warn] `video_title` not returned by `youtube-dl`")

    ini_path = out_dir / f"{filename}.ini"
    with open(ini_path, "w") as configfile:
        config.write(configfile)

    return Path(out_dir / f"{filename}.{ext}"), ini_path
