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
    guid: str
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
    guid: str
    learning: str
    english: str
    audio: str
    frame: str
    video_title: str
    video_url: str
    tags: str
