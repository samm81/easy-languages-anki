#!/usr/bin/env python3
import argparse

from easy_languages_anki import segmentize, config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="find segments in easy-language video")
    parser.add_argument("video_path", type=str, help="path to the video file")
    parser.add_argument("language", type=str, help="language to do ocr with")
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
    parser.add_argument(
        "--outfile",
        "-o",
        type=str,
        default="20_segments_raw.csv",
        help="path to the output file",
    )

    args = parser.parse_args()

    # easy-language videos translations are always english
    language = f"{args.language}+eng"

    segmentize.segmentize(
        args.video_path,
        language,
        args.outfile,
        args.caption_video_similarity_cutoff,
        args.caption_text_similarity_cutoff,
    )

    print("done!")
