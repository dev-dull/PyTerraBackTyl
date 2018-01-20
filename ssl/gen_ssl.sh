#!/bin/bash

# Check for `openssl`
wssl=`which openssl`
wissl=`whereis openssl | awk '{print $2}'`

# Set the options -- force the password to be empty
opts='req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout private.key -out public.key -passout pass:'

if [ -x "$wssl" ]; then
  $wssl $opts
elif [ -x "$wissl" ]; then
  $wissl $opts
else
  echo "Whoops! I couldn't find the openssl command. Verify that it is installed and that your PATH variable includes the location of the command."
  exit 1
fi
