#!/bin/bash

###########
# Set your logging directory and ensure the service account has read/write access. 
# Otherwise, a new 'logs' directory will be created in program's path.
###########

LOGGING_DIR="logs"


###########
pg_dir=`cd $(dirname $0) && pwd`

cd "$pg_dir"
mkdir -p "$LOGGING_DIR"
nohup python3 pyterrabacktyl.py 2>&1 > "$LOGGING_DIR/pyterrabacktyl.log" &
echo
