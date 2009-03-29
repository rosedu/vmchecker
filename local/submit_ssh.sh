#!/bin/bash
# An example script to submit a homework to queue manager

# address of queue manager machine
ADDRESS=sanctuary

# vmchecker user on remote machine
USER=so

# location of vmchecker on remote machine
VMCHECKER_ROOT=/home/so/vmchecker/vmchecker


# copies the file and notifies (implicit) queue manager
scp "$1" $USER@$ADDRESS:$VMCHECKER_ROOT/queue/
echo "Sending "$1" to "$USER@$ADDRESS:$VMCHECKER_ROOT/queue/
unzip -l "$1"
