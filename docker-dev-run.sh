#!/bin/sh

dirname=$(basename "$PWD")
dirname_lower=$(echo "$dirname" | tr '[:upper:]' '[:lower:]')
IMAGE_NAME="local-${dirname_lower}"

#PORT_HOST='57541'
#PORT_CONTAINER='8080'
#  -p "${PORT_HOST:?PORT_HOST not set}:${PORT_CONTAINER:?PORT_CONTAINER not set}" \

docker run \
  --interactive --tty \
  --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):/app" \
  -v "${HOME}/xorkspace/${dirname}:/app/vids" \
  "$IMAGE_NAME" \
  "$@"
