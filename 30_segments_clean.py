import csv
from contextlib import contextmanager
import argparse
from typing import Generator, Callable

from segment import SegmentRawText, Segment


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


SegmentsRawGenerator = Generator[SegmentRawText, None, None]


def segments_raw_from_csv(filename) -> SegmentsRawGenerator:
    yield from map(SegmentRawText._make, csv_rows(filename))


SegmentsGenerator = Generator[Segment, None, None]


def segments_from_segments_raw(segments_raw: SegmentsRawGenerator) -> SegmentsGenerator:
    for num, start_timestamp, end_timestamp, text in segments_raw:
        polish_english = text.split("\n", 1)
        polish, english = (
            (polish_english[0], "") if len(polish_english) == 1 else polish_english
        )
        yield Segment(num, start_timestamp, end_timestamp, polish, english)


def merge_segments(segment_prev: Segment, curr_segment: Segment) -> Segment:
    return Segment(
        segment_prev.num,
        segment_prev.start_timestamp,
        curr_segment.end_timestamp,
        f"{segment_prev.polish} {curr_segment.polish}",
        f"{segment_prev.english} {curr_segment.english}",
    )


def edit_segment(segment: Segment) -> Segment:
    split = input("beginning of english text: ")
    polish, english = segment.polish.split(split, 1)
    return Segment(**segment, polish=polish, english=f"{split}{english}")


def segment_handle(
    segment_prev: Segment,
    segment_curr: Segment,
    segment_save: Callable[[Segment], None],
) -> Segment:
    print(segment_curr)
    command = input("[k]eep (default), [m]erge, [d]r[o]p, [e]dit ? ").lower()

    if command == "m":
        segment = merge_segments(segment_prev, segment_curr)
        print("merged")
        print(segment)
    elif command == "d" or command == "o":
        segment = segment_prev
        print("discarded")
    elif command == "e":
        segment = edit_segment(segment)
        print("edited")
        return segment_handle(segment_prev, segment)
    else:
        segment = segment_curr
        print("kept")

        segment_save(segment_prev)

    return segment


def main(input_file, output_file):
    segments_raw = segments_raw_from_csv(input_file)
    segments = segments_from_segments_raw(segments_raw)

    segment_prev = next(segments)
    segment_handle(Segment(0, 0, 0, "", ""), segment_prev, lambda _: None)

    with csv_rowwriter(output_file, "w") as writerow:
        writerow(Segment._fields)

    def segment_save(segment: Segment) -> None:
        with csv_rowwriter(output_file, "a") as writerow:
            writerow(segment)

    for segment in segments:
        segment_prev = segment_handle(segment_prev, segment, segment_save)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="clean found segments")
    parser.add_argument("--infile", "-i", type=str, default="20_segments.csv")
    parser.add_argument("--outfile", "-o", type=str, default="30_segments_cleaned.csv")
    args = parser.parse_args()

    main(args.infile, args.outfile)

    print("done!")
