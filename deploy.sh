#!/bin/bash
# upload project to vps2

remote_host="vps2"
local_host="lpb-air.local"

# rebuild production
function sync_docker {
    rsync --progress --ignore-existing -a docker-compose_prod.yml "$remote_host":docker/docker-compose.yml
    rsync --progress -a env "$remote_host":docker/
    rsync --progress -a --delete-after helper_scripts "$remote_host":docker/
    rsync --progress -a --delete-after nginx "$remote_host":docker/
    rsync --progress -a --delete-after \
        --exclude config.json.sample \
        --exclude __pycache__ \
        --exclude static/dyn \
        web "$remote_host":docker/

    ssh "$remote_host" 'docker compose -f docker/docker-compose.yml up -d --build'

}

# rebuild testing
function sync_test {
    
    ssh "$local_host" "mkdir -p docker"

    rsync --progress --ignore-existing -a docker-compose_testing.yml "$local_host":docker/docker-compose.yml
    rsync --progress -a env "$local_host":docker/
    rsync --progress -a --delete-after helper_scripts "$local_host":docker/
    rsync --progress -a --delete-after nginx "$local_host":docker/
    rsync --progress -a --delete-after \
        --exclude config.json.sample \
        --exclude __pycache__ \
        --exclude static/dyn \
        web "$local_host":docker/

    ssh "$local_host" 'docker compose -f docker/docker-compose.yml up -d --build'

}

if [[ $1 == "test" ]]; then
    sync_test "$2"
elif [[ $1 == "docker" ]]; then
    sync_docker
else
    echo "valid options are: test | docker"
fi

##
exit 0
