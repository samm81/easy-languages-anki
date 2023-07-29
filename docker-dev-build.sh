#!/bin/sh

dirname=$(basename "$PWD")
dirname_lower=$(echo "$dirname" | tr '[:upper:]' '[:lower:]')
IMAGE_NAME="local-${dirname_lower}"

DOCKERFILE_NAME='dev.Dockerfile'

docker buildx build \
  --file "$DOCKERFILE_NAME" \
  --tag "$IMAGE_NAME" \
  .

if [ "$?" -eq 0 ]
then
  notify-send "$IMAGE_NAME built !"
else
  notify-send "$IMAGE_NAME failed !"
fi
