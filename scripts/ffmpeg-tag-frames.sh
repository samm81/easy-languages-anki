#!/bin/sh
# unnofficial POSIX shell strict mode
set -o errexit
set -o nounset

IFS=$(printf '\n\t')

[ "${TRACE:-0}" = "1" ] && set -o xtrace

usage() {
  filename="$(basename "$0")"
  echo "Usage: ./${filename} <video file>"
  exit
}

[ "${1:-}" = "--help" ] && usage

cd "$(dirname "$0")"

main() {
  video="${1:?missing video file}"
  video_name="$(basename "$video")"
  video_location="$(dirname "$video")"
  video_out="${video_location}/${video_name%.*}-frames.mp4"
  ffmpeg \
    -i "$video" \
    -vf "drawtext=fontfile=/usr/share/fonts/TTF/DejaVuSerif.ttf: text=%{n}: x=(w-tw)/2: y=h-(2*lh): fontcolor=white: box=1: boxcolor=0x00000099" \
    -y "$video_out"
}

main "$@"

exit 0
