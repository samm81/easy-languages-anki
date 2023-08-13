import cv2
from skimage.metrics import structural_similarity as ssim
from typing import Generator, Optional, Tuple
import numpy as np
import argparse
import itertools
import subprocess
from PIL import Image
import pytesseract
import csv
from contextlib import contextmanager

from segment import SegmentRawText

Frame = np.ndarray

FrameGenerator = Generator[Frame, None, None]


def frame_generator(video: cv2.VideoCapture) -> FrameGenerator:
    while True:
        ret: bool
        frame_color: Optional[Frame]
        ret, frame_color = video.read()
        if ret:
            frame_bw = cv2.cvtColor(frame_color, cv2.COLOR_BGR2GRAY)
            yield frame_bw
        else:
            break


FramePair = Tuple[Frame, Frame, int]
FramePairGenerator = Generator[FramePair, None, None]


def frame_pair_generator(
    frame_generator: FrameGenerator,
) -> FramePairGenerator:
    frame_prev = next(frame_generator)
    for frame_num, frame in enumerate(frame_generator, start=1):
        yield (frame_prev, frame, frame_num)
        frame_prev = frame


Segment = Tuple[int, int, float, Frame]
SegmentGenerator = Generator[Segment, None, None]


def segment_finder(
    frame_generator: FramePairGenerator, similarity_cutoff: float
) -> SegmentGenerator:
    segment_start: int = 0
    for frame_prev, frame, frame_num in frame_generator:
        frame_prev_subtitle_region = extract_subtitle_region(frame_prev)
        score: float
        _diff: Frame
        score, _diff = ssim(
            frame_prev_subtitle_region,
            extract_subtitle_region(frame),
            full=True,
        )

        if score < similarity_cutoff:
            yield (segment_start, frame_num - 1, score, frame_prev_subtitle_region)
            segment_start = frame_num


def extract_subtitle_region(frame: Frame) -> Frame:
    h, w = frame.shape
    subtitle_region = frame[int(0.78 * h) : int(0.92 * h), 0:w]
    return subtitle_region


SegmentWithText = Tuple[int, int, str]
SegmentWithTextGenerator = Generator[SegmentWithText, None, None]


def segments_add_text_generator(
    segments: SegmentGenerator,
) -> SegmentWithTextGenerator:
    for segment_start, segment_end, _score, subtitle_region in segments:
        image = Image.fromarray(np.uint8(subtitle_region))
        text = pytesseract.image_to_string(image, lang="pol").strip()
        yield (segment_start, segment_end, text)


SegmentWithTexts = Tuple[int, int, set[str]]
SegmentWithTextsGenerator = Generator[SegmentWithTexts, None, None]


def segments_join_on_text(
    segments: SegmentWithTextGenerator,
    caption_similarity_cutoff: int,
) -> SegmentWithTextsGenerator:
    segment_start_start, segment_start_end, segment_start_text = next(segments)
    segment_prev: SegmentWithTexts = (
        segment_start_start,
        segment_start_end,
        set([segment_start_text]),
    )
    for segment in segments:
        # print("segment_prev", segment_prev)
        # print("segment", segment)
        segment_prev_start, _segment_prev_end, segment_prev_texts = segment_prev
        segment_start, segment_end, segment_text = segment
        if any(
            levenshtein_similarity(segment_prev_text, segment_text)
            > caption_similarity_cutoff
            for segment_prev_text in segment_prev_texts
        ):
            segments_merged = (
                segment_prev_start,
                segment_end,
                segment_prev_texts | set([segment_text]),
            )
            segment = segments_merged
            # print("similar merged", segment)
        else:
            yield segment_prev
            segment = (segment_start, segment_end, set([segment_text]))

        segment_prev = segment


def levenshtein_similarity(str1, str2):
    distance = levenshtein_distance(str1, str2)
    if distance == 0:
        return 1

    similarity = 1 - (distance / max(len(str1), len(str2)))
    return similarity


# chatgpt generated
def levenshtein_distance(str1, str2):
    if len(str1) < len(str2):
        return levenshtein_distance(str2, str1)

    if len(str2) == 0:
        return len(str1)

    previous_row = range(len(str2) + 1)
    for i, c1 in enumerate(str1):
        current_row = [i + 1]
        for j, c2 in enumerate(str2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def texts_average(texts: set[str]) -> str:
    levenshtein_distances_from_all = (
        (
            text,
            sum(levenshtein_distance(text, other) for other in texts if text != other),
        )
        for text in texts
    )
    text_smallest_dist, _smallest_dist = min(
        levenshtein_distances_from_all, key=lambda x: x[1]
    )

    return text_smallest_dist


@contextmanager
def csv_rowwriter(filename, mode):
    with open(filename, mode, newline="") as f:
        yield csv.writer(f).writerow


def main(
    video_path: str,
    similarity_cutoff: float,
    caption_similarity_cutoff: int,
    outfile: str,
) -> None:
    video: cv2.VideoCapture = cv2.VideoCapture(video_path)

    fps: float = video.get(cv2.CAP_PROP_FPS)

    frame_gen: FrameGenerator = frame_generator(video)
    frame_pair_gen: FramePairGenerator = frame_pair_generator(frame_gen)
    segments_gen: SegmentGenerator = segment_finder(frame_pair_gen, similarity_cutoff)
    segments_with_text: SegmentWithTextGenerator = segments_add_text_generator(
        segments_gen
    )
    segments_joined_text: SegmentWithTextsGenerator = segments_join_on_text(
        segments_with_text, caption_similarity_cutoff
    )
    segments_has_text: SegmentWithTextsGenerator = (
        (start, end, texts)
        for start, end, texts in segments_joined_text
        if texts != set([""])
    )
    segments_no_short: SegmentWithTextGenerator = (
        (start, end, texts)
        for start, end, texts in segments_has_text
        if end - start > 3
    )
    segments_average_text: SegmentWithTextGenerator = (
        (start, end, texts_average(texts)) for start, end, texts in segments_no_short
    )
    segments_out = segments_average_text

    with csv_rowwriter(outfile, "w") as writerow:
        writerow(SegmentRawText._fields)

    for segment_start_frame, segment_end_frame, text in segments_out:
        segment = SegmentRawText(segment_start_frame, segment_end_frame, text)
        with csv_rowwriter(outfile, "a") as writerow:
            writerow(segment)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="find segments in easy-polish video")
    parser.add_argument("video_path", type=str, help="path to the video file")
    parser.add_argument(
        "--similarity-cutoff",
        type=float,
        default=0.97,
        help=(
            "value between -1 and 1 below which the scene is considered to be changed"
            " (-1 means total dissimilarity and 1 means they're identical)"
        ),
    )
    parser.add_argument(
        "--caption-similarity-cutoff",
        type=float,
        default=0.7,
        help=(
            "minumum levenshtein similarity between captions to be considered the same"
            " (0 means total dissimilarity and 1 means they're identical)"
        ),
    )
    parser.add_argument(
        "--outfile",
        "-o",
        type=str,
        default="20_segments.csv",
        help="path to the output file",
    )

    args = parser.parse_args()

    main(
        args.video_path,
        args.similarity_cutoff,
        args.caption_similarity_cutoff,
        args.outfile,
    )

    print("done!")
