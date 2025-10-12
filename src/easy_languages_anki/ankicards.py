import configparser
import csv
import os
import subprocess
from collections.abc import Iterable
from contextlib import contextmanager

import cv2
from tqdm import tqdm

from .segment import (
    AnkiVideoFrameCard,
    AnkiVideoFrameCardReqs,
    AnkiVideoFullCard,
    AnkiVideoFullCardReqs,
    Segment,
)

FPS = 30


@contextmanager
def csv_rowwriter(filename, mode):
    with open(filename, mode, newline="") as f:
        yield csv.writer(f).writerow


def csv_rows(filename):
    with open(filename, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == [*Segment._fields]
        yield from reader


def segments_from_csv(filename) -> Iterable[Segment]:
    return tqdm([Segment._make(row) for row in csv_rows(filename)], unit="segment")


def read_ini(video_ini_path: str) -> tuple[str, str, str]:
    config = configparser.ConfigParser()
    config.read(video_ini_path)
    video_id = config["video"]["id"]
    video_title = config["video"]["title"]
    video_url = config["video"]["url"]
    return video_id, video_title, video_url


def timestamp_format(timestamp: float) -> str:
    return f"{timestamp:07.2f}".replace(".", "_")


def id_anki_card_for_segment(
    video_id: str, start_timestamp: float, end_timestamp: float
) -> str:
    start_timestamp_str = timestamp_format(start_timestamp)
    end_timestamp_str = timestamp_format(end_timestamp)
    return f"{video_id}-{start_timestamp_str}-{end_timestamp_str}"


def outfile_path_and_name(
    video_path: str,
    id_anki_card: str,
    extension: str,
) -> tuple[str, str]:
    outfile_name = f"{id_anki_card}.{extension}"

    video_dirname = os.path.dirname(video_path)
    outfile = os.path.join(video_dirname, outfile_name)

    return outfile, outfile_name


def segment_video(
    video_path: str,
    id_anki_card: str,
    segment_start_timestamp: float,
    segment_end_timestamp: float,
) -> str:
    outfile, outfile_name = outfile_path_and_name(video_path, id_anki_card, "webm")

    _completed_process = subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-loglevel",
            "error",
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
        ],
        check=True,
    )

    return outfile_name


def segment_audio(
    video_path: str,
    id_anki_card: str,
    segment_start_timestamp: float,
    segment_end_timestamp: float,
) -> str:
    outfile, outfile_name = outfile_path_and_name(video_path, id_anki_card, "aac")

    _completed_process = subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-loglevel",
            "error",
            "-y",  # overwrite output file
            "-i",
            video_path,
            "-ss",  # start
            str(segment_start_timestamp),
            "-to",  # to
            str(segment_end_timestamp),
            "-vn",  # no video
            "-acodec",
            "copy",  # copy audio without re-encoding
            outfile,
        ],
        check=True,
    )

    return outfile_name


def segment_frame(
    video: cv2.VideoCapture,
    frame_number: int,
    video_path: str,
    video_id: str,
    segment_start_timestamp: float,
    segment_end_timestamp: float,
) -> str:
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
    ret, image = video.read()

    if not ret:
        raise RuntimeError(f"could not read frame {frame_number}")

    id_anki_card = id_anki_card_for_segment(
        video_id, segment_start_timestamp, segment_end_timestamp
    )

    outfile, outfile_name = outfile_path_and_name(video_path, id_anki_card, "jpg")

    cv2.imwrite(outfile, image)

    return outfile_name


def segment_to_anki_video_full_card_reqs(
    segment: Segment,
    video_path: str,
    video_id: str,
    video_title: str,
    video_url: str,
    fps: float,
) -> AnkiVideoFullCardReqs:
    start_frame_s, end_frame_s, learning, english = segment
    start_frame, end_frame = int(start_frame_s), int(end_frame_s)

    start_timestamp, end_timestamp = start_frame / fps, end_frame / fps

    id_anki_card = id_anki_card_for_segment(video_id, start_timestamp, end_timestamp)

    video_name = segment_video(
        video_path,
        id_anki_card,
        start_timestamp,
        end_timestamp,
    )

    return AnkiVideoFullCardReqs(
        learning=learning,
        english=english,
        video=video_name,
        video_title=video_title,
        video_url=video_url,
        id_anki_card=id_anki_card,
    )


def anki_video_full_card_reqs_to_anki_video_full_cards(
    anki_card_reqs: AnkiVideoFullCardReqs,
) -> AnkiVideoFullCard:
    learning, english, video, video_title, video_url, id_anki_card = anki_card_reqs

    return AnkiVideoFullCard(
        learning=learning,
        english=english,
        video=video,
        video_media_anchor=f"[sound:{video}]",
        video_title=video_title,
        video_url=video_url,
        cloze_listen_hack="{{c1::}}",
        priority=str(len(f"{learning} {english}")),
        id_anki_card=id_anki_card,
        tags="",
    )


def segment_to_anki_video_frame_card_reqs(
    segment: Segment,
    video: cv2.VideoCapture,
    video_path: str,
    video_id: str,
    video_title: str,
    video_url: str,
    fps: float,
) -> AnkiVideoFrameCardReqs:
    start_frame_s, end_frame_s, learning, english = segment
    start_frame, end_frame = int(start_frame_s), int(end_frame_s)

    start_timestamp, end_timestamp = start_frame / fps, end_frame / fps

    id_anki_card = id_anki_card_for_segment(video_id, start_timestamp, end_timestamp)

    audio_name = segment_audio(
        video_path,
        id_anki_card,
        start_timestamp,
        end_timestamp,
    )

    mid_frame = (start_frame + end_frame) // 2
    frame_name = segment_frame(
        video, mid_frame, video_path, video_id, start_timestamp, end_timestamp
    )

    return AnkiVideoFrameCardReqs(
        learning=learning,
        english=english,
        audio=audio_name,
        frame=frame_name,
        video_title=video_title,
        video_url=video_url,
        id_anki_card=id_anki_card,
    )


def anki_video_frame_card_reqs_to_anki_video_frame_cards(
    anki_card_reqs: AnkiVideoFrameCardReqs,
) -> AnkiVideoFrameCard:
    learning, english, audio, frame, video_title, video_url, id_anki_card = (
        anki_card_reqs
    )

    return AnkiVideoFrameCard(
        learning=learning,
        english=english,
        audio=audio,
        frame=frame,
        video_title=video_title,
        video_url=video_url,
        id_anki_card=id_anki_card,
        tags="",
    )


def segments_to_video_cards(
    video_path: str,
    video_ini_path: str,
    input_file: str,
    output_file: str,
):
    video_id, video_title, video_url = read_ini(video_ini_path)

    segments = segments_from_csv(input_file)

    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)

    anki_card_reqs = (
        segment_to_anki_video_full_card_reqs(
            segment, video_path, video_id, video_title, video_url, fps
        )
        for segment in segments
    )
    anki_cards = (
        anki_video_full_card_reqs_to_anki_video_full_cards(anki_card_reqs)
        for anki_card_reqs in anki_card_reqs
    )

    with csv_rowwriter(output_file, "w") as writerow:
        writerow(AnkiVideoFullCard._fields)

    with csv_rowwriter(output_file, "a") as writerow:
        for anki_card in anki_cards:
            writerow(anki_card)


def segments_to_frame_cards(
    video_path: str,
    video_ini_path: str,
    input_file: str,
    output_file: str,
):
    video_id, video_title, video_url = read_ini(video_ini_path)

    segments = segments_from_csv(input_file)

    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)

    anki_card_reqs = (
        segment_to_anki_video_frame_card_reqs(
            segment, video, video_path, video_id, video_title, video_url, fps
        )
        for segment in segments
    )
    anki_cards = (
        anki_video_frame_card_reqs_to_anki_video_frame_cards(anki_card_reqs)
        for anki_card_reqs in anki_card_reqs
    )

    with csv_rowwriter(output_file, "w") as writerow:
        writerow(AnkiVideoFrameCard._fields)

    for anki_card in anki_cards:
        with csv_rowwriter(output_file, "a") as writerow:
            # raise RuntimeError("have to fix audio and frame field")
            writerow(anki_card)
