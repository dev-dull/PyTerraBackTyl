#!/bin/bash

pg_dir=`cd $(dirname $0) && pwd`
cd "$pg_dir"

# Generate SSL keys if none are found
if [ ! -f ssl/public.key ]; then
    openssl req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout ssl/private.key -out ssl/public.key -passout "pass:" -subj "/C=US/ST=Portland/L=ORn/O=PyTerraBackTYLy/OU=dev_dull/CN="
fi

# Generate SSH keys if none are found
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa <<< y > /dev/null 2>&1
fi

echo GIT BACKEND USERS: Please make note of your public SSH key >&2
cat ~/.ssh/id_rsa.pub >&2

python3 pyterrabacktyl.py

