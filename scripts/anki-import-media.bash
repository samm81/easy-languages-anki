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
  echo "usage: ./${filename} <search_dir> <dest_dir>"
  exit
}

[[ "${1:-}" =~ ^-*h(elp)?$ ]] && usage

main() {
  local search_dir dest_dir
  search_dir="${1:?missing \`search_dir\`}"
  dest_dir="${2:?missing \`dest_dir\`}"
  /bin/find "$search_dir" -type f \( -name '*.aac' -o -name '*.jpg' \) -exec cp -t "$dest_dir" {} +
}

main "$@"

exit 0
