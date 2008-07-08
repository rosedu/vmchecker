#!/bin/bash

umask 0000
ulimit -t 120

while [ -f /proc/`cat /tmp/checker.pid`/exe ]; do
    sleep 1;
done

echo $$ > /tmp/checker.pid

exec /bin/bash -c " $@ "
