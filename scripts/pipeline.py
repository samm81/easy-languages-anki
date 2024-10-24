#!/usr/bin/env python3
import argparse
from pathlib import Path

from easy_languages_anki import videodl, segmentize, segmentcleaner, ankicards, config


def main(
    video_youtube_id: str,
    video_out_dir: Path,
    lang: str,
    segments_raw_text_file: Path,
    segments_cleaned_file: Path,
    ankicards_file: Path,
    caption_video_similarity_cutoff: float,
    caption_text_similarity_cutoff: float,
):
    print(f"downloading video {video_youtube_id} to {video_out_dir}")
    video_path, video_ini_path = videodl.download_youtube(
        video_youtube_id, video_out_dir
    )
    print(f"segmentizing video {video_path}")
    segmentize.segmentize(
        str(video_path),
        lang,
        str(segments_raw_text_file),
        caption_video_similarity_cutoff,
        caption_text_similarity_cutoff,
    )
    print("cleaning segments")
    segmentcleaner.clean(segments_raw_text_file, segments_cleaned_file)
    print("generating anki cards")
    ankicards.segments_to_frame_cards(
        str(video_path),
        str(video_ini_path),
        str(segments_cleaned_file),
        str(ankicards_file),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video_id", type=Path, help="id of youtube video")
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("lang", type=str)
    parser.add_argument(
        "--caption-video-similarity-cutoff",
        type=float,
        default=config.SEGMENTIZE_CAPTION_VIDEO_SIMILARITY_CUTOFF_DEFAULT,
        help=config.SEGMENTIZE_CAPTION_VIDEO_SIMILARITY_CUTOFF_HELP,
    )
    parser.add_argument(
        "--caption-text-similarity-cutoff",
        type=float,
        default=config.SEGMENTIZE_CAPTION_TEXT_SIMILARITY_CUTOFF_DEFAULT,
        help=config.SEGMENTIZE_CAPTION_TEXT_SIMILARITY_CUTOFF_HELP,
    )
    args = parser.parse_args()

    # easy-languages videos are always captioned in the target language and english
    lang = f"{args.lang}+eng"

    workdir = args.out_dir / args.video_id
    video_out_dir = workdir
    segments_raw_text_file = workdir / "pipeline_10_segments_raw.csv"
    segments_cleaned_file = workdir / "pipeline_20_segments_cleaned.csv"
    ankicards_file = workdir / "pipeline_30_ankicards.csv"

    workdir.mkdir(parents=True, exist_ok=True)

    main(
        args.video_id,
        video_out_dir,
        lang,
        segments_raw_text_file,
        segments_cleaned_file,
        ankicards_file,
        args.caption_video_similarity_cutoff,
        args.caption_text_similarity_cutoff,
    )

    print("done!")
