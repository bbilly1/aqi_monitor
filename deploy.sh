#!/bin/bash
# upload project to vps2

rsync --progress -a docker-compose.yml vps2:docker/
rsync --progress -a env vps2:docker/
rsync --progress -a --delete-after helper_scripts vps2:docker/
rsync --progress -a --delete-after nginx vps2:docker/
rsync --progress -a --delete-after --exclude config.json.sample --exclude __pycache__ --exclude static/dyn \
    web vps2:docker/

##
exit 0
