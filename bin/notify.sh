#!/bin/sh
if [ "x$1" = "x" ]; then
    echo "$0: missing course_id argument"
    echo "    correct syntax: $0 course_id"
    exit 1
fi

echo "NOTIFY: calling semctl up" $1
./semctl up $1

exit 0