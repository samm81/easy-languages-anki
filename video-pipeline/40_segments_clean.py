import csv
from contextlib import contextmanager
import argparse
from typing import Generator, Callable, Iterable

from segment import SegmentRawText, Segment
from editor import drop_user_into_editor


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


def merge_segments(
    segment_prev: Segment, curr_segment: SegmentRawText
) -> SegmentRawText:
    prev_polish, prev_english = segment_prev.polish, segment_prev.english
    edit_text = f"{prev_polish}\n{prev_english}\n{curr_segment.text}"

    curr_polish_english = curr_segment.text.split("\n")
    if len(curr_polish_english) == 2:
        curr_polish, curr_english = curr_polish_english
        edit_text = f"{prev_polish}\n{curr_polish}\n{prev_english}\n{curr_english}"

    return SegmentRawText(segment_prev.start_frame, curr_segment.end_frame, edit_text)


def fixup_segments(segment_prev: Segment, curr_segment: SegmentRawText) -> Segment:
    return Segment(
        segment_prev.start_frame,
        curr_segment.end_frame,
        segment_prev.polish,
        segment_prev.english,
    )


def edit_segment_raw(segment: SegmentRawText) -> SegmentRawText:
    start_frame, end_frame, text = segment
    text_new = drop_user_into_editor(text).strip()
    return SegmentRawText(start_frame, end_frame, text_new)


def segment_raw_text_to_segment(segment_raw: SegmentRawText) -> Segment:
    start_frame, end_frame, text = segment_raw
    polish_english = text.split("\n")
    if len(polish_english) != 2:
        raise ValueError("expected polish and english separated by newline")
    polish, english = polish_english
    return Segment(start_frame, end_frame, polish, english)


def segment_raw_handle(
    segment_prev: Segment,
    segment_curr: SegmentRawText,
    segment_save: Callable[[Segment], None],
) -> Segment:
    print(segment_curr)

    start_frame, end_frame, text = segment_curr
    polish_english = text.split("\n")
    if len(polish_english) != 2:
        command = input("[e]dit (default), [m]erge, [f]ixup, [d]r[o]p ? ").lower()
        command = "e" if command == "" else command
    else:
        command = input(
            "[k]eep (default), [e]dit, [m]erge, [f]ixup, [d]r[o]p ? "
        ).lower()
        command = "k" if command == "" else command

    if command == "m":
        segment = merge_segments(segment_prev, segment_curr)
        segment = edit_segment_raw(segment)
        return segment_raw_text_to_segment(segment)
    if command == "f":
        return fixup_segments(segment_prev, segment_curr)
    elif command == "d" or command == "o":
        print("discarded")
        return segment_prev
    elif command == "e":
        segment = edit_segment_raw(segment_curr)
        print("edited")
        segment_save(segment_prev)
        return segment_raw_text_to_segment(segment)
    elif command == "k":
        print("kept")
        segment_save(segment_prev)
        return segment_raw_text_to_segment(segment_curr)

    raise ValueError(f"unknown command: {command}")


def main(input_file, output_file, non_interactive, start_frame):
    segments_raw = segments_raw_from_csv(input_file)
    segments_raw = (
        segment_raw
        for segment_raw in segments_raw
        if int(segment_raw.start_frame) >= start_frame
    )

    if start_frame == 0:
        with csv_rowwriter(output_file, "w") as writerow:
            writerow(Segment._fields)

    def segment_save(segment: Segment) -> None:
        with csv_rowwriter(output_file, "a") as writerow:
            writerow(segment)

    if non_interactive:
        raise NotImplementedError("`non_interactive` mode not implemented yet")

    # bug where if first segment is dropped, the no-op save handler is replaced
    segment_prev = segment_raw_handle(
        Segment(0, 0, "", ""), next(segments_raw), lambda _: None
    )
    for segment_raw in segments_raw:
        segment_prev = segment_raw_handle(segment_prev, segment_raw, segment_save)

    segment_save(segment_prev)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="clean found segments")
    parser.add_argument("--infile", "-i", type=str, default="20_segments.csv")
    parser.add_argument("--outfile", "-o", type=str, default="30_segments_cleaned.csv")
    parser.add_argument("--non-interactive", type=bool, default=False)
    parser.add_argument("--start-frame", type=int, default=0)
    args = parser.parse_args()

    main(args.infile, args.outfile, args.non_interactive, args.start_frame)

    print("done!")
