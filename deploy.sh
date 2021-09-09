#!/bin/bash
# upload project to vps2

host="vps2"

rsync --progress -a docker-compose.yml "$host":docker/
rsync --progress -a env "$host":docker/
rsync --progress -a --delete-after helper_scripts "$host":docker/
rsync --progress -a --delete-after nginx "$host":docker/
rsync --progress -a --delete-after \
    --exclude config.json.sample \
    --exclude __pycache__ \
    --exclude static/dyn \
    web "$host":docker/

ssh "$host" 'docker build -t bbilly1/lpb-air:latest docker/web'
ssh "$host" 'docker-compose -f docker/ up -d'

##
exit 0
