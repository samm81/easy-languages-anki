#!/usr/bin/env python3
import argparse
from enum import IntEnum, unique
from pathlib import Path

from easy_languages_anki import ankicards, config, segmentcleaner, segmentize, videodl


def pipeline_video_download(video_id: str, video_out_dir: Path):
    video_path, video_ini_path = videodl.download_youtube(video_id, video_out_dir)
    return video_path, video_ini_path


def pieline_segmentize(
    video_path: Path,
    lang: str,
    segments_raw_text_file: Path,
    caption_video_similarity_cutoff: float,
    caption_text_similarity_cutoff: float,
):
    segmentize.segmentize(
        str(video_path),
        lang,
        str(segments_raw_text_file),
        caption_video_similarity_cutoff,
        caption_text_similarity_cutoff,
    )


def pipeline_clean_segments(segments_raw_text_file: Path, segments_cleaned_file: Path):
    segmentcleaner.clean(segments_raw_text_file, segments_cleaned_file)


def video_generate_anki_cards(
    video_path: Path,
    video_ini_path: Path,
    segments_cleaned_file: Path,
    ankicards_file: Path,
):
    ankicards.segments_to_frame_cards(
        str(video_path),
        str(video_ini_path),
        str(segments_cleaned_file),
        str(ankicards_file),
    )


@unique
class PipelineStage(IntEnum):
    VIDEO_DOWNLOAD = 1
    SEGMENTIZE = 2
    SEGMENTS_CLEAN = 3
    ANKI_CARDS = 4
    DONE = 5


def pipeline(
    video_id: str,
    out_dir: Path,
    lang: str,
    caption_video_similarity_cutoff: float,
    caption_text_similarity_cutoff: float,
):
    # easy-languages videos are always captioned in the target language and english
    lang = f"{lang}+eng"

    workdir = out_dir / video_id
    video_out_dir = workdir
    segments_raw_text_file = workdir / "pipeline_20_segments_raw.csv"
    segments_cleaned_file = workdir / "pipeline_40_segments_cleaned.csv"
    ankicards_file = workdir / "pipeline_50_ankicards.csv"

    workdir.mkdir(parents=True, exist_ok=True)

    stage = PipelineStage.VIDEO_DOWNLOAD
    video_path = video_out_dir / f"{video_id}.mp4"
    video_ini_path = video_out_dir / f"{video_id}.ini"
    if video_path.exists() and video_ini_path.exists():
        if segments_raw_text_file.exists():
            if segments_cleaned_file.exists():
                if ankicards_file.exists():
                    stage = PipelineStage.DONE
                else:
                    stage = PipelineStage.ANKI_CARDS
            else:
                stage = PipelineStage.SEGMENTS_CLEAN
        else:
            stage = PipelineStage.SEGMENTIZE

    print(f"video_id: {video_id}")
    print(f"starting from stage: {stage.name}")

    while stage != PipelineStage.DONE:
        if stage == PipelineStage.VIDEO_DOWNLOAD:
            video_path, video_ini_path = pipeline_video_download(
                video_id, video_out_dir
            )
        elif stage == PipelineStage.SEGMENTIZE:
            print(f"segmentizing video {video_path}")
            pieline_segmentize(
                video_path,
                lang,
                segments_raw_text_file,
                caption_video_similarity_cutoff,
                caption_text_similarity_cutoff,
            )
        elif stage == PipelineStage.SEGMENTS_CLEAN:
            print("cleaning segments")
            pipeline_clean_segments(segments_raw_text_file, segments_cleaned_file)
        elif stage == PipelineStage.ANKI_CARDS:
            print("generating anki cards")
            video_generate_anki_cards(
                video_path, video_ini_path, segments_cleaned_file, ankicards_file
            )
        else:
            raise ValueError(f"unknown stage: {stage}")

        stage = stage + 1

    print("done!")


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

    pipeline(
        args.video_id,
        args.out_dir,
        args.lang,
        args.caption_video_similarity_cutoff,
        args.caption_text_similarity_cutoff,
    )
