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
  echo "usage: ./${filename} <english_file> <anki_cards_csv>"
  echo '  pulls all cards from `anki_cards_csv` matching `english_file`' \
       'preserving order'
  exit
}

[[ "${1:-}" =~ ^-*h(elp)?$ ]] && usage

main() {
  english_file="${1:?missing \`english_file\`}"
  anki_cards_csv="${2:?missing \`anki_cards_csv\`}"
  while read -r english; do
    qsv search --literal --select 'english' "$english" "$anki_cards_csv"
  done < "$english_file"
}

main "$@"

exit 0
