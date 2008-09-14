#!/bin/bash

echo "COMMANDER called with " $1
exec $VMCHECKER_ROOT/Commander/commander "$1"
