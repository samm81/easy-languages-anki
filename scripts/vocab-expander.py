#!/usr/bin/env python3
import argparse
from pathlib import Path

import anki
from anki.parser import AnkiNoteEasyLanguages
from easy_languages_anki import segment
from vocab import expander, vocab


def main(notes_csv_anki_export: Path, notes_csv_easy_language: Path):
    notes_anki = anki.parser.notes_from_notes_txt(
        AnkiNoteEasyLanguages, notes_csv_anki_export
    )
    vocab_known = vocab.from_strings(note.target for note in notes_anki)
    notes_easy_language = segment.anki_video_frame_cards_from_csv(
        notes_csv_easy_language
    )
    expand_diff = expander.ankicards_diff_from_known_vocab(
        vocab_known, notes_easy_language
    )
    diff_size, cards = next(expand_diff)
    cards_by_len = sorted(cards, key=lambda card: len(card.learning))

    segment.anki_video_frame_cards_to_csv(
        Path(f"./expander-cards-{diff_size}.csv"), cards_by_len
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("notes_csv_anki_export", type=Path)
    parser.add_argument("notes_csv_easy_language", type=Path)
    args = parser.parse_args()

    main(args.notes_csv_anki_export, args.notes_csv_easy_language)
