#!/usr/bin/env bash
# unofficial strict mode
# note bash<=4.3 chokes on empty arrays with set -o nounset
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
# https://sharats.me/posts/shell-script-best-practices/
set -o errexit
set -o nounset
set -o pipefail

IFS=$'\n\t'
shopt -s nullglob globstar

[[ "${TRACE:-0}" == '1' ]] && set -o xtrace

usage() {
  local filename
  filename="$(basename "$0")"
  echo "Usage: ./${filename} <video_ids_file> <out_dir>"
  echo '  `pipeline.py` but for all `video_id`s in `video_ids_file`'
  exit
}

[[ "${1:-}" =~ ^-*h(elp)?$ ]] && usage

main() {
  video_ids_file="${1:?missing arg \`video_ids_file\`}"
  out_dir="${2:?missing arg \`out_dir\`}"
  lang="${3:?missing arg \`lang\`}"
  while read -r video_id; do
    [[ -d "${out_dir}/${video_id}" ]] && echo "[warn] skipping existing ${out_dir}/${video_id}" && continue
    "$(dirname "$0")/pipeline.py" "${video_id}" "${out_dir}" "${lang}"
  done < "${video_ids_file}"
}

main "$@"

exit 0
