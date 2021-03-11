#!/bin/bash
# upload project to vps2

rsync --progress -a docker-compose.yml vps2:docker/
rsync --progress -a env vps2:docker/
rsync --progress -a --delete-after helper_scripts vps2:docker/
rsync --progress -a --delete-after \
    --exclude dyn --exclude config.sample --exclude __pychache__ \
    backend vps2:docker/
rsync --progress -a --delete-after \
    --exclude dyn \
    frontend vps2:docker/

##
exit 0
