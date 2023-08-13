import argparse
import configparser
import youtube_dl
from os import path


def main(video_id, outdir):
    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "format": "best",
        "outtmpl": path.join(outdir, f"{video_id}.%(ext)s"),
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_title = info.get("title")

    if not video_title:
        print("[WARNING] `video_title` not returned by youtube-dl")

    config = configparser.ConfigParser()
    config["video"] = {
        "url": url,
        "id": video_id,
        "title": video_title,
    }

    with open(path.join(outdir, f"{video_id}.ini"), "w") as configfile:
        config.write(configfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video_id", help="id of youtube video")
    parser.add_argument("--outdir", default="/vids")
    args = parser.parse_args()

    main(args.video_id, args.outdir)
