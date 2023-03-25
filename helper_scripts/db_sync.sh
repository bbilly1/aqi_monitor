#!/bin/bash
# sync production db to local testing vm

remote_host="vps2"
local_host="lpb-air.local"

echo "---------------------------------------"
echo "sync aqi db from $remote_host to $local_host"
echo "---------------------------------------"

# download
printf "\n  -> backup\n"
ssh $remote_host 'docker exec postgres pg_dump -U aqi | gzip > backup.gz'
printf "\n  -> download\n"
rsync --progress -r --remove-source-files -e ssh $remote_host:backup.gz /tmp/backup.gz

# sync
printf "\n  -> sync\n"
rsync --progress -r --remove-source-files /tmp/backup.gz -e ssh $local_host:backup
ssh $local_host 'gzip -df backup/backup.gz'

# replace
printf "\n  -> replace\n"

ssh $local_host "docker exec -i postgres psql -U aqi -c \
    'DROP SCHEMA public CASCADE;'"
ssh $local_host "docker exec -i postgres psql -U aqi -c \
    'CREATE SCHEMA public;'"

ssh $local_host "docker exec -i postgres psql -U aqi -c \
    'DROP TABLE IF EXISTS aqi;'"
ssh $local_host "docker exec -i postgres psql -U aqi -c \
    'DROP TABLE IF EXISTS weather;'"
ssh $local_host 'docker exec -i postgres psql -U aqi -d aqi < backup/backup'
ssh $local_host "trash backup/backup"
printf "\n  -> done\n"

##
exit 0
