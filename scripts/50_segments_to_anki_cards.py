#!/usr/bin/env python3
import argparse

from easy_languages_anki import ankicards

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="clean found segments")
    parser.add_argument("video_path", type=str, help="path to the video file")
    parser.add_argument("video_ini_path", type=str, help="path to the video ini file")
    parser.add_argument("--infile", "-i", type=str, default="40_segments_cleaned.csv")
    parser.add_argument("--outfile", "-o", type=str, default="50_anki_cards.csv")
    parser.add_argument(
        "--use-full-video",
        help="use full video instead of a frame",
        type=bool,
        default=False,
    )
    args = parser.parse_args()

    if args.use_full_video:
        ankicards.segments_to_video_cards(
            args.video_path, args.video_ini_path, args.infile, args.outfile
        )
    else:
        ankicards.segments_to_frame_cards(
            args.video_path, args.video_ini_path, args.infile, args.outfile
        )

    print("done!")
