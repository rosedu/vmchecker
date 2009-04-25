#!/bin/sh
# Notify - ups a semaphore to notify the queue_manager

if [ -z $1 ]; then
    echo "[NOTIFY.SH] Usage: $0 course_id"
    exit 1
fi

echo "[NOTIFY.SH] received new homework for $1"
`dirname $0`/semctl up $1
