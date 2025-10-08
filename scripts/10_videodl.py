#!/usr/bin/env python3
import argparse
from pathlib import Path

from easy_languages_anki import videodl

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video_id", help="id of youtube video")
    parser.add_argument("out_dir")
    args = parser.parse_args()

    videodl.download_youtube(args.video_id, Path(args.out_dir))

    print("done!")
