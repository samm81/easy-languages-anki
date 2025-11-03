# easy-languages-anki

cut up videos from the easy-languages youtube channels, parse out subtitles, turn into anki cards.

### setup

1. install [`tesseract`][1]
1. install `ffmpeg`
1. use your `pyproject`-compatible python package manager of choice to install dependencies
1. (inside your `venv`) `make setup`
1. (inside your `venv`) `pip install -e .`

[1]: https://github.com/tesseract-ocr/tesseract

### usage

`./scripts/pipeline.py` to turn a single video into notes, `./scripts/pipeline-multi-bash` to turn multuple videos into notes, `./scripts/vocab-expander.py` to find which notes to import.

### cognates

from https://github.com/vsoto/cognates_en_es/blob/8b157d54261c26d739123a383defcde05c99bfd8/cognates_en_es.csv
