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

# Set the user information so Git won't complain
# (when not set, git exits with non-zero, raising service exception)
user_name=`git config user.name`
if [ -z "$user_name" ]; then
    if [ -z "$GIT_USER_NAME" ]; then
        GIT_USER_NAME="pyterrabacktyl"
    fi
    git config --global user.name "$GIT_USER_NAME"
fi

user_email=`git config user.email`
if [ -z "$user_email" ]; then
    if [ -z "$GIT_USER_EMAIL" ]; then
        GIT_USER_EMAIL="pyterrabacktyl@devdull.lol"  # Default to script author's domain.
    fi
    git config --global user.email "$GIT_USER_EMAIL"
fi


echo GIT BACKEND USERS: Please make note of your public SSH key >&2
cat ~/.ssh/id_rsa.pub >&2

/env/bin/python3 pyterrabacktyl.py

