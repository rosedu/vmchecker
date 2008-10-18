#!/bin/bash

echo "======================================================"
echo "======================================================"

echo "[COMMANDER.SH] called with " $1
exec $VMCHECKER_ROOT/Commander/commander "$1"
