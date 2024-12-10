from itertools import groupby
from collections.abc import Iterable, Iterator

from easy_languages_anki.segment import AnkiVideoFrameCard
from vocab import vocab
from vocab.vocab import Vocab


def ankicards_diff_from_known_vocab(
    vocab_known: Vocab, cards: Iterable[AnkiVideoFrameCard]
) -> Iterator[tuple[int, Iterator[AnkiVideoFrameCard]]]:
    card_diffs = (
        (card, ankicard_diff_from_known_vocab(vocab_known, card)) for card in cards
    )
    diff_groups = groupby(
        sorted(card_diffs, key=lambda cd: cd[1]), key=lambda cd: cd[1]
    )
    return (
        (diff_size, (card[0] for card in cards)) for diff_size, cards in diff_groups
    )


def ankicard_diff_from_known_vocab(vocab_known: Vocab, card: AnkiVideoFrameCard) -> int:
    vocab_card = vocab.from_string(card.learning)
    return len(vocab_card - vocab_known)
