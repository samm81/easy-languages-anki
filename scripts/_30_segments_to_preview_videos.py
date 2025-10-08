#!/usr/bin/env python3

# unfinished and experimental

import argparse
import csv
from collections.abc import Iterable
from contextlib import contextmanager

from segment import SegmentRawText, SegmentRawVideo


@contextmanager
def csv_rowwriter(filename, mode):
    with open(filename, mode, newline="") as f:
        yield csv.writer(f).writerow


def csv_rows(filename):
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == [*SegmentRawText._fields]
        yield from reader


def segments_raw_from_csv(filename) -> Iterable[SegmentRawText]:
    return map(SegmentRawText._make, csv_rows(filename))


def segment_raw_text_to_segment_raw_video(
    segment_raw: SegmentRawText, video_path: str
) -> SegmentRawVideo:
    start_frame, end_frame, text = segment_raw
    return SegmentRawVideo(start_frame, end_frame, polish, english, video_path)


def main(input_file, output_file):
    segments_raw = segments_raw_from_csv(input_file)

    with csv_rowwriter(output_file, "w") as writerow:
        writerow(SegmentRawVideo._fields)

    raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="make video slices for found segments")
    parser.add_argument("--infile", "-i", type=str, default="segments.csv")
    parser.add_argument("--outfile", "-o", type=str, default="segments_videos.csv")
    args = parser.parse_args()

    main(args.infile, args.outfile)

    print("done!")
