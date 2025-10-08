import csv
from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple

# all types are `str` because we're often reading these out of `csv` files


class SegmentRawText(NamedTuple):
    start_frame: str
    end_frame: str
    text: str


class Segment(NamedTuple):
    start_frame: str
    end_frame: str
    learning: str
    english: str


class AnkiVideoFullCardReqs(NamedTuple):
    learning: str
    english: str
    video: str
    video_title: str
    video_url: str


class AnkiVideoFrameCardReqs(NamedTuple):
    learning: str
    english: str
    audio: str
    frame: str
    video_title: str
    video_url: str


class AnkiVideoFullCard(NamedTuple):
    learning: str
    english: str
    video: str
    video_media_anchor: str
    video_title: str
    video_url: str
    cloze_listen_hack: str
    priority: str
    tags: str


class AnkiVideoFrameCard(NamedTuple):
    learning: str
    english: str
    audio: str
    frame: str
    video_title: str
    video_url: str
    tags: str


def anki_video_frame_cards_from_csv(csv_path: Path) -> Iterable[AnkiVideoFrameCard]:
    with open(csv_path, mode="r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == [*AnkiVideoFrameCard._fields]
        yield from (AnkiVideoFrameCard._make(row) for row in reader)


def anki_video_frame_cards_to_csv(
    csv_path: Path, cards: Iterable[AnkiVideoFrameCard]
) -> None:
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(AnkiVideoFrameCard._fields)
        for learning, english, audio, frame, video_title, video_url, tags in cards:
            writer.writerow(
                (
                    learning,
                    english,
                    f"[sound:{audio}]",
                    f"<img src='{frame}'>",
                    video_title,
                    video_url,
                    tags,
                )
            )
