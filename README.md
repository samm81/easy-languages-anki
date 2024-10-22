cut up videos from the easy-polish youtube channel, parse out subtitles, turn
into anki cards. may work for other easy-language videos as well, untested.

### setup

1. install [`tesseract`][1]
1. install `ffmpeg`
1. `pdm install` (or use the `dev.Dockerfile` and `docker-dev-run.sh` script)

### usage

creating a deck:

1. go through the pipeline in order in `video-pipeline/`
1. copy resultant csv to `brain-brew/src/data`, resultant videos/images to
   `brain-brew/src/media`
1. in `brain-brew/` `pdm run brainbrew run recipies/source_to_anki.yml`

updating a deck:

1. go through the pipeline in order in `video-pipeline/` to generate new cards
1. export your deck in crowdanki format
1. edit `brain-brew/recipies/anki_to_source.yml` to point it at export directory
1. (maybe) `rm -r brain-brew/src/`
1. in `brain-brew/` `pdm run brainbrew run recipies/anki_to_source.yml`
1. `cat` new cards onto `brain-brew/src/data` csv file, copy media files to `brain-brew/src/media`
1. in `brain-brew/` `pdm run brainbrew run recipies/source_to_anki.yml`

theoretically should work!

[1]: https://github.com/tesseract-ocr/tesseract
