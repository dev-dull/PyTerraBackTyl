#!/bin/bash

# Set the options -- force the password to be empty
opts='req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout private.key -out public.key -passout pass:'

# find, goto, and ensure permissions on the directory.
d=`cd $(dirname $0) && pwd`  # get the path that this script is in.
cd "$d"
e=`echo $? | tr -d '-'`  # get the ABS of the exit code the lazy way.
touch .x  # create the empty file .x to ensure write permissions on the dir
let e=$e+`echo $? | tr -d '-'`
rm .x  # cleanup and make sure that went okay too
let e=$e+`echo $? | tr -d '-'`

if [ $e != 0 ]; then
  echo "Looks like you don't have the right permissions set on $d" >&2
  exit $e
fi

# Check for `openssl`
# `which` and `whereis` sometimes check different places, so use both to look.
wssl=`which openssl`
wissl=`whereis openssl | awk '{print $2}'`
# use the non-printing system-bell character to separate results and grab a working answer
ssl_app=`echo -e "\a$wssl\a$wissl\a" | grep -Pio "\a[^\a]+\a" | head -n 1 | tr -d "\a"`

if [ -x "$ssl_app" ]; then
  $ssl_app $opts
  chmod 600 private.key
  exit 0
fi

echo "Either openssl wasn't found, or the command was not executable by $USER" >&2
exit -1

