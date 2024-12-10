import sys
from collections.abc import Iterable

import spacy

nlp = spacy.load("es_core_news_md")

type Vocab = set[str]


def from_string(text: str) -> Vocab:
    return set(
        token.lemma_
        for token in nlp(text.lower())
        if not token.is_punct and not token.is_space
    )


def from_strings(texts: Iterable[str]) -> Vocab:
    return set(word for text in texts for word in from_string(text))


if __name__ == "__main__":
    sentences = sys.stdin.readlines()
    vocab = from_strings(sentences)
    print(vocab)
