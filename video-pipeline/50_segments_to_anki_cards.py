from contextlib import contextmanager
from typing import Iterable
import argparse
import csv
import os
import subprocess
import configparser

from segment import Segment, AnkiCardReqs, AnkiCard


@contextmanager
def csv_rowwriter(filename, mode):
    with open(filename, mode, newline="") as f:
        yield csv.writer(f).writerow


def csv_rows(filename):
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == [*Segment._fields]
        yield from reader


def segments_from_csv(filename) -> Iterable[Segment]:
    return map(Segment._make, csv_rows(filename))


def timestamp_format(timestamp: float):
    return f"{timestamp:07.2f}".replace(".", "_")


def segment_video(
    video_path: str,
    video_id: str,
    segment_start_timestamp: float,
    segment_end_timestamp: float,
):
    video_dirname = os.path.dirname(video_path)
    segment_start_timestamp_str = timestamp_format(segment_start_timestamp)
    segment_end_timestamp_str = timestamp_format(segment_end_timestamp)
    outfile_name = (
        f"{video_id}-{segment_start_timestamp_str}-{segment_end_timestamp_str}.webm"
    )
    outfile = os.path.join(video_dirname, outfile_name)

    subprocess.call(
        [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-ss",  # start
            str(segment_start_timestamp),
            "-to",  # to
            str(segment_end_timestamp),
            "-c:v",  # video codec
            "libvpx-vp9",  # webm vp9
            "-crf",  # quality for constant quality mode. The CRF value can be from 0–63. Lower values mean better quality. 41 is a recommended starting point for the VP9 codec.
            "41",
            "-b:v",  # allow bitrate to vary in order to achieve the quality specified by -crf
            "0",
            "-vf",
            "scale=-1:360",  # changes the height of the video to 360 pixels and keeps the aspect ratio of the input video.
            "-c:a",  # audio codec
            "libopus",
            outfile,
        ]
    )

    return outfile_name


def segment_to_anki_card_reqs(
    segment: Segment, video_path: str, video_id: str, video_title: str, video_url: str
) -> AnkiCardReqs:
    start_frame, end_frame, polish, english = segment

    fps = 30

    start_timestamp, end_timestamp = int(start_frame) / fps, int(end_frame) / fps

    video_name = segment_video(
        video_path,
        video_id,
        start_timestamp,
        end_timestamp,
    )

    return AnkiCardReqs(
        polish=polish,
        english=english,
        video=video_name,
        video_title=video_title,
        video_url=video_url,
    )


def anki_card_reqs_to_anki_cards(anki_card_reqs: AnkiCardReqs) -> AnkiCard:
    polish, english, video, video_title, video_url = anki_card_reqs

    return AnkiCard(
        guid="",
        polish=polish,
        english=english,
        video=video,
        video_media_anchor=f"[sound:{video}]",
        video_title=video_title,
        video_url=video_url,
        cloze_listen_hack="{{c1::}}",
        priority=len(f"{polish} {english}"),
        tags="",
    )


def main(video_path, video_ini_path, input_file, output_file):
    config = configparser.ConfigParser()
    config.read(video_ini_path)
    video_id = config["video"]["id"]
    video_title = config["video"]["title"]
    video_url = config["video"]["url"]

    segments = segments_from_csv(input_file)
    anki_card_reqs = (
        segment_to_anki_card_reqs(segment, video_path, video_id, video_title, video_url)
        for segment in segments
    )
    anki_cards = (
        anki_card_reqs_to_anki_cards(anki_card_reqs)
        for anki_card_reqs in anki_card_reqs
    )

    with csv_rowwriter(output_file, "w") as writerow:
        writerow(AnkiCard._fields)

    for anki_card in anki_cards:
        with csv_rowwriter(output_file, "a") as writerow:
            writerow(anki_card)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="clean found segments")
    parser.add_argument("video_path", type=str, help="path to the video file")
    parser.add_argument("video_ini_path", type=str, help="path to the video ini file")
    parser.add_argument("--infile", "-i", type=str, default="segments_cleaned.csv")
    parser.add_argument("--outfile", "-o", type=str, default="anki_cards.csv")
    args = parser.parse_args()

    main(args.video_path, args.video_ini_path, args.infile, args.outfile)

    print("done!")
