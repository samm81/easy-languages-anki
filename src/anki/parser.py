import csv
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple, TextIO, TypeVar


def notes_csv(f: TextIO) -> Iterable[Iterable[str]]:
    next(f)  # separator:tab
    next(f)  # html:false
    reader = csv.reader(f, delimiter="\t")
    yield from reader


NoteType = TypeVar("NoteType", bound=NamedTuple)


def notes_from_io(notetype: type[NoteType], f: TextIO) -> Iterable[NoteType]:
    return (notetype._make(row) for row in notes_csv(f))


def notes_from_notes_txt(
    notetype: type[NoteType], note_txt_path: Path
) -> Iterable[NoteType]:
    with open(note_txt_path, "r", newline="") as f:
        yield from notes_from_io(notetype, f)


class AnkiNoteEasyLanguages(NamedTuple):
    target: str
    english: str
    english_literal: str
    extra: str
    audio: str
    frame: str
    video_title: str
    video_url: str
    lang: str


if __name__ == "__main__":
    for note in notes_from_io(AnkiNoteEasyLanguages, sys.stdin):
        print(note.target)
