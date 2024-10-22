#!/usr/bin/env python3
import argparse

from easy_languages_anki import segmentcleaner

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="clean found segments")
    parser.add_argument("--infile", "-i", type=str, default="20_segments_raw.csv")
    parser.add_argument("--outfile", "-o", type=str, default="40_segments_cleaned.csv")
    parser.add_argument(
        "--interactive", type=bool, default=False, action=argparse.BooleanOptionalAction
    )
    parser.add_argument("--start-frame", type=int, default=0)
    args = parser.parse_args()

    if args.start_frame and not args.interactive:
        print("[warn] `start_frame` is ignored when `interactive` is `False`")

    if args.interactive:
        segmentcleaner.clean_interactively(args.infile, args.outfile, args.start_frame)
    else:
        segmentcleaner.clean(args.infile, args.outfile)

    print("done!")
