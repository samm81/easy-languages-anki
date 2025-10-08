import csv
from collections.abc import Generator, Iterator
from contextlib import contextmanager

import cv2
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm

from . import config, imagetotext
from .segment import SegmentRawText

Frame = np.ndarray


def frame_generator(video: cv2.VideoCapture) -> Generator[Frame, None, None]:
    while True:
        ret: bool
        frame_color: Frame | None
        ret, frame_color = video.read()
        if ret:
            frame_bw = cv2.cvtColor(frame_color, cv2.COLOR_BGR2GRAY)
            yield frame_bw
        else:
            break


FramePair = tuple[Frame, Frame, int]


def frame_pair_generator(
    frame_generator: Iterator[Frame],
) -> Iterator[FramePair]:
    frame_prev = next(frame_generator)
    for frame_num, frame in enumerate(frame_generator, start=1):
        yield (frame_prev, frame, frame_num)
        frame_prev = frame


Segment = tuple[int, int, float, Frame]


def segment_finder(
    frame_generator: Iterator[FramePair], caption_video_similarity_cutoff: float
) -> Iterator[Segment]:
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

        if score < caption_video_similarity_cutoff:
            yield (segment_start, frame_num - 1, score, frame_prev_subtitle_region)
            segment_start = frame_num


def extract_subtitle_region(frame: Frame) -> Frame:
    h, w = frame.shape
    subtitle_region = frame[int(0.78 * h) : int(0.92 * h), 0:w]
    return subtitle_region


SegmentWithText = tuple[int, int, str]


def segments_add_text_generator(
    segments: Iterator[Segment],
    lang: str,
) -> Iterator[SegmentWithText]:
    for segment_start, segment_end, _score, subtitle_region in segments:
        image = Image.fromarray(np.uint8(subtitle_region))
        text = imagetotext.video_frame_extract_text(image, lang)
        yield (segment_start, segment_end, str(text))


SegmentWithTexts = tuple[int, int, set[str]]


def segments_join_on_text(
    segments: Iterator[SegmentWithText],
    caption_text_similarity_cutoff: float,
) -> Iterator[SegmentWithTexts]:
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
            > caption_text_similarity_cutoff
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


def segmentize(
    video_path: str,
    lang: str,
    outfile: str,
    caption_video_similarity_cutoff: float = config.SEGMENTIZE_CAPTION_VIDEO_SIMILARITY_CUTOFF_DEFAULT,
    caption_text_similarity_cutoff: float = config.SEGMENTIZE_CAPTION_TEXT_SIMILARITY_CUTOFF_DEFAULT,
) -> None:
    video: cv2.VideoCapture = cv2.VideoCapture(video_path)

    # fps: float = video.get(cv2.CAP_PROP_FPS)

    frames_total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_gen: Iterator[Frame] = iter(
        tqdm(frame_generator(video), total=frames_total, unit="frame")
    )
    frame_pair_gen: Iterator[FramePair] = frame_pair_generator(frame_gen)
    segments_gen: Iterator[Segment] = segment_finder(
        frame_pair_gen, caption_video_similarity_cutoff
    )
    segments_with_text: Iterator[SegmentWithText] = segments_add_text_generator(
        segments_gen, lang
    )
    segments_joined_text: Iterator[SegmentWithTexts] = segments_join_on_text(
        segments_with_text, caption_text_similarity_cutoff
    )
    segments_has_text: Iterator[SegmentWithTexts] = (
        (start, end, texts)
        for start, end, texts in segments_joined_text
        if texts != set([""])
    )
    segments_no_short: Iterator[SegmentWithTexts] = (
        (start, end, texts)
        for start, end, texts in segments_has_text
        if end - start > 3
    )
    segments_average_text: Iterator[SegmentWithText] = (
        (start, end, texts_average(texts)) for start, end, texts in segments_no_short
    )
    segments_out = segments_average_text

    with csv_rowwriter(outfile, "w") as writerow:
        writerow(SegmentRawText._fields)

    for segment_start_frame, segment_end_frame, text in segments_out:
        segment = SegmentRawText(str(segment_start_frame), str(segment_end_frame), text)
        with csv_rowwriter(outfile, "a") as writerow:
            writerow(segment)
