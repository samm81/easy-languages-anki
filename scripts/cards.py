#!/usr/bin/env python3
import csv
import sys
from contextlib import contextmanager
from collections.abc import Iterable

from easy_languages_anki.segment import AnkiVideoFrameCard


@contextmanager
def csv_rowwriter(filename, mode):
    with open(filename, mode, newline="") as f:
        yield csv.writer(f).writerow


def csv_rows(filename):
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == [*AnkiVideoFrameCard._fields]
        yield from reader


def ankicards_from_csv(filename) -> Iterable[AnkiVideoFrameCard]:
    return map(AnkiVideoFrameCard._make, csv_rows(filename))


def ankicards_search(
    ankicards: Iterable[AnkiVideoFrameCard], search: str
) -> Iterable[AnkiVideoFrameCard]:
    searchl = search.lower()
    return filter(lambda card: searchl in card.english.lower(), ankicards)


def ankicards_sort(
    ankicards: Iterable[AnkiVideoFrameCard],
) -> Iterable[AnkiVideoFrameCard]:
    return sorted(ankicards, key=ankicard_complexity_length)


def ankicard_complexity_length(ankicard: AnkiVideoFrameCard) -> int:
    return len(ankicard.english)


if __name__ == "__main__":
    cards = ankicards_from_csv("ankicards-all.csv")
    cards_coffee = ankicards_search(cards, "coffee")
    cards_sorted = ankicards_sort(cards_coffee)
    writer = csv.writer(sys.stdout)
    for target, english, audio, frame, video_title, video_url, tags in cards_sorted:
        writer.writerow(
            [
                target,
                english,
                f"[sound:{audio}]",
                f"<img src='{frame}'>",
                video_title,
                video_url,
                "esp",
                tags,
            ]
        )
