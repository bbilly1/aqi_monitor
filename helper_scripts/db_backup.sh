#!/bin/bash
# greate postgres backup and status log

time_stamp=$(date '+%Y%m%d')
time_date=$(date '+%Y%m%d_%H%M%S')
backup_dir="$HOME/backup"

# backup
docker exec postgres pg_dump -U aqi | gzip > "$backup_dir/pg_$time_stamp.gz"

# log
log_file="$backup_dir/pg_status_$time_stamp.log"

query="SELECT schemaname AS table_schema, \
       relname AS table_name, \
       pg_size_pretty(pg_relation_size(relid)) AS data_size \
FROM pg_catalog.pg_statio_user_tables \
ORDER BY pg_relation_size(relid) DESC;"

echo "postgres dump run at $time_date" > "$log_file"
docker exec postgres psql -U aqi -c "$query" >> "$log_file"

##
exit 0
