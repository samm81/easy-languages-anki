from collections import namedtuple

SegmentRawText = namedtuple(
    "SegmentRawText", ["num", "start_timestamp", "end_timestamp", "text"]
)

Segment = namedtuple(
    "Segment", ["num", "start_timestamp", "end_timestamp", "polish", "english"]
)
