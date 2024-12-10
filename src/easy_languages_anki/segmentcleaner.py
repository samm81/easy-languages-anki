import csv
from contextlib import contextmanager
from collections.abc import Iterable, Callable

from .segment import SegmentRawText, Segment
from .editor import drop_user_into_editor


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
    prev_learning, prev_english = segment_prev.learning, segment_prev.english
    edit_text = f"{prev_learning}\n{prev_english}\n{curr_segment.text}"

    curr_learning_english = curr_segment.text.split("\n")
    if len(curr_learning_english) == 2:
        curr_learning, curr_english = curr_learning_english
        edit_text = f"{prev_learning}\n{curr_learning}\n{prev_english}\n{curr_english}"

    return SegmentRawText(segment_prev.start_frame, curr_segment.end_frame, edit_text)


def fixup_segments(segment_prev: Segment, curr_segment: SegmentRawText) -> Segment:
    return Segment(
        segment_prev.start_frame,
        curr_segment.end_frame,
        segment_prev.learning,
        segment_prev.english,
    )


def edit_segment_raw(segment: SegmentRawText) -> SegmentRawText:
    start_frame, end_frame, text = segment
    text_new = drop_user_into_editor(text).strip()
    return SegmentRawText(start_frame, end_frame, text_new)


def segment_raw_text_to_segment(segment_raw: SegmentRawText) -> Segment:
    start_frame, end_frame, text = segment_raw
    if not segment_raw_is_valid(segment_raw):
        raise ValueError("expected learning and english separated by newline")
    learning, english = text.split("\n")
    return Segment(start_frame, end_frame, learning, english)


def segment_raw_is_valid(segment: SegmentRawText) -> bool:
    return len(segment.text.split("\n")) == 2


def segment_raw_handle_interactive(
    segment_prev: Segment,
    segment_curr: SegmentRawText,
    segment_save: Callable[[Segment], None],
) -> Segment:
    print(segment_curr)

    if not segment_raw_is_valid(segment_curr):
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


def segment_raw_handle_non_interactive(
    segment: SegmentRawText,
    segment_save: Callable[[Segment], None],
) -> None:
    if segment_raw_is_valid(segment):
        segment_save(segment_raw_text_to_segment(segment))
    else:
        print(f"[warn] dropping invalid segment: {segment}")


def clean_interactively(input_file, output_file, start_frame):
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

    # bug where if first segment is dropped, the no-op save handler is replaced
    segment_prev = segment_raw_handle_interactive(
        Segment("0", "0", "", ""), next(segments_raw), lambda _: None
    )
    for segment_raw in segments_raw:
        segment_prev = segment_raw_handle_interactive(
            segment_prev, segment_raw, segment_save
        )

    segment_save(segment_prev)


def clean(input_file, output_file):
    segments_raw = segments_raw_from_csv(input_file)

    with csv_rowwriter(output_file, "w") as writerow:
        writerow(Segment._fields)

    def segment_save(segment: Segment) -> None:
        with csv_rowwriter(output_file, "a") as writerow:
            writerow(segment)

    for segment_raw in segments_raw:
        segment_raw_handle_non_interactive(segment_raw, segment_save)
