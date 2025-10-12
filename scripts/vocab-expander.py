#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Optional

import anki
from anki.parser import AnkiNoteEasyLanguages
from easy_languages_anki import segment
from vocab import expander, vocab


def main(
    notes_csv_anki_export: Path,
    notes_csv_easy_language: Path,
    know_vocab_list: Optional[Path],
):
    notes_anki_gen = anki.parser.notes_from_notes_txt(
        AnkiNoteEasyLanguages, notes_csv_anki_export
    )
    notes_anki = list(notes_anki_gen)

    vocab_known = vocab.from_strings(note.target for note in notes_anki)
    notes_easy_language = segment.anki_video_frame_cards_from_csv(
        notes_csv_easy_language
    )
    expand_diff = expander.ankicards_diff_from_known_vocab(
        vocab_known, notes_easy_language
    )
    diff_size, cards_ = next(expand_diff)
    cards = list(cards_)
    print(f"{len(cards)=}")

    already_know_card_ids = {note.id_anki_card for note in notes_anki}
    print(f"{len(already_know_card_ids)=}")

    cards_not_already_know = [
        card for card in cards if card.id_anki_card not in already_know_card_ids
    ]
    print(f"{len(cards_not_already_know)=}")

    cards_by_len = sorted(cards_not_already_know, key=lambda card: len(card.learning))

    segment.anki_video_frame_cards_to_csv(
        Path(f"./expander-cards-{diff_size}.csv"), cards_by_len
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("notes_csv_anki_export", type=Path)
    parser.add_argument("notes_csv_easy_language", type=Path)
    parser.add_argument(
        "--known_vocab_list",
        type=Path,
        required=False,
        help="Optional path to known vocabulary list",
    )
    args = parser.parse_args()

    main(
        args.notes_csv_anki_export, args.notes_csv_easy_language, args.known_vocab_list
    )
