#!/bin/bash

## CONFIG SECTION
PORT=2442


# You shouldn't need to modify anything below this line.

pid=`curl -s http://localhost:$PORT/getpid`
while [ "$pid" == "False" ]
do
  echo "A terrform action is in progress. Will try again in 5 seconds."
  sleep 5
  pid=`curl -s http://localhost:$PORT/shutdown`
done

kill $pid
