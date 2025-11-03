#!/usr/bin/env python3
import argparse
from pathlib import Path

import anki
from anki.parser import AnkiNoteEasyLanguages
from easy_languages_anki import segment
from vocab import expander, vocab


def _file_to_vocab(file: Path) -> vocab.Vocab:
    vocab = set()
    with file.open("r", encoding="utf-8") as f:
        for line in f:
            if line.lstrip().startswith("#"):
                continue  # Skip comment lines

            words = line.strip().split()
            vocab.update(words)
    return vocab


def main(
    notes_csv_easy_language: Path,
    notes_csv_anki_export: Path,
    num_expansions: int,
    outfile_prefix: str,
    notes_csv_skip: Path | None,
    known_vocab_list: Path | None,
):
    notes_anki = list(
        anki.parser.notes_from_notes_txt(AnkiNoteEasyLanguages, notes_csv_anki_export)
    )

    vocab_known = vocab.from_strings(note.target for note in notes_anki)

    if known_vocab_list:
        vocab_know_manual = _file_to_vocab(known_vocab_list)
        vocab_known.update(vocab_know_manual)

    notes_easy_language = segment.anki_video_frame_cards_from_csv(
        notes_csv_easy_language
    )

    already_know_ids = {note.id_anki_card for note in notes_anki}
    notes_easy_language = (
        note
        for note in notes_easy_language
        if note.id_anki_card not in already_know_ids
    )

    if notes_csv_skip:
        notes_skip = segment.anki_video_frame_cards_from_csv(notes_csv_skip)
        notes_skip_ids = {note.id_anki_card for note in notes_skip}

        notes_easy_language = (
            note
            for note in notes_easy_language
            if note.id_anki_card not in notes_skip_ids
        )

    expand_diff = expander.ankicards_diff_from_known_vocab(
        vocab_known, notes_easy_language
    )

    for expansion_num in range(num_expansions):
        diff_size, notes_ = next(expand_diff)
        notes = list(notes_)
        print(f"{expansion_num=} {len(notes)=}")

        notes_by_len = sorted(notes, key=lambda note: len(note.learning))

        segment.anki_video_frame_cards_to_csv(
            Path(f"./{outfile_prefix}-{diff_size}.csv"), notes_by_len
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("notes_csv_anki_export", type=Path)
    parser.add_argument(
        "notes_csv_easy_language",
        type=Path,
    )
    parser.add_argument(
        "--known-vocab-list",
        type=Path,
        required=False,
        help="optional path to file containing already known spanish words",
    )
    parser.add_argument(
        "--skip-notes",
        type=Path,
        required=False,
        help="optional path to file containing list of notes to skip",
    )
    parser.add_argument(
        "--num-expansions",
        type=int,
        default=1,
        help="number of expansions to generate (default 1)",
    )
    parser.add_argument(
        "--outfile-prefix",
        type=str,
        default="expander-cards",
        help="outfile name: `{prefix}-{expansion}.csv` (default 'expander-cards')",
    )
    args = parser.parse_args()

    main(
        args.notes_csv_easy_language,
        args.notes_csv_anki_export,
        args.num_expansions,
        args.outfile_prefix,
        args.skip_notes,
        args.known_vocab_list,
    )
