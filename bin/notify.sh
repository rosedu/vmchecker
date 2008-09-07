#!/bin/sh
# Notify - ups a semaphore to notify the queue_manager
# Lucian Adrian Grijincu (lucian.grijincu@gmail.com)

if [ -z $1 ]; then
    echo "Usage: $0 course_id"
    exit 1
fi

echo "received new homework for" $1
./semctl up $1
