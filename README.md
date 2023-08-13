cut up videos from the easy-polish youtube channel, parse out subtitles, turn
into anki cards. may work for other easy-language videos as well, untested.

1. `poetry install` (or use the `dev.Dockerfile` and `docker-dev-run.sh`
   script)
1. go through the pipeline in order in `video-pipeline/`
1. copy resultant csv to `brain-brew/src/data`, resultant video to
   `brain-brew/src/media`
1. navigate to `brain-brew/` and `poetry run brainbrew run
recipies/source_to_anki.yml`

theoretically should work!
