from collections import namedtuple

SegmentRawText = namedtuple("SegmentRawText", ["start_frame", "end_frame", "text"])

Segment = namedtuple("Segment", ["start_frame", "end_frame", "polish", "english"])

AnkiCardReqs = namedtuple(
    "AnkiCard", ["polish", "english", "video", "video_title", "video_url"]
)

AnkiCard = namedtuple(
    "AnkiCard",
    [
        "guid",
        "polish",
        "english",
        "video",
        "video_media_anchor",
        "video_title",
        "video_url",
        "cloze_listen_hack",
        "priority",
        "tags",
    ],
)
