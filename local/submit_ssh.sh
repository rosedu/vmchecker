#!/bin/bash
# An example script to submit a homework to queue manager

# address of queue manager machine
ADDRESS=192.168.1.2

# vmchecker user on remote machine
USER=vmchecker

# location of vmchecker on remote machine
VMCHECKER_ROOT=/home/vmchecker/vmchecker


# copies the file and notifies queue manager
echo scp $1 $USER@$ADDRESS:$VMCHECKER_ROOT/queue/
echo ssh $USER@$ADDRESS bash -c "cd $VMCHECKER_ROOT && bin/notify.sh"
