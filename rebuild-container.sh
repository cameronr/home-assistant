#!/bin/bash

# set -x

UPDATE=
VERSION=0.91.4

#https://stackoverflow.com/questions/14786984/best-way-to-parse-command-line-args-in-bash
while getopts "u" opt; do
  case $opt in
    u)
      UPDATE=yes
      ;;

  esac
done

if [ "$UPDATE" == "yes" ]; then
  docker pull homeassistant/home-assistant:latest
fi

docker rm -f home-assistant >&/dev/null

docker run \
  -d \
  --name home-assistant \
  --net=host \
  -v /volume1/docker/home-assistant:/config \
  --restart=always \
  --device=/dev/ttyACM0 \
  --privileged=true \
  homeassistant/home-assistant:$VERSION
