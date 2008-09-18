#!/bin/bash

# Queue Manager
# Author: Lucian Adrian Grijincu (lucian.grijincu@gmail.com)
# Copyright (c) 2008 rosedu.org
# See LICENSE file for copyright and license details.
#
# TODO:
#  - hwconf_queue_dir should not be passed as argument, but
#    computed from environment variable VMCHECKER_ROOT
#  - semaphore should be created if it doesn't exist
#  - at notify all homeworks in directory should checked

# the directory where the homework config files are stored.
hwconf_queue_dir=$VMCHECKER_ROOT/queue

# the id of the course. It's used to identify the semaphore.
course_id=$1

# path to the commander (gets tests.zip & file.zip and runs the vmexecutor)
commander=`dirname $0`/commander.sh

# path to the IPC semaphore manipulator
semctl=`dirname $0`/semctl

notifier=`dirname $0`/notify.sh


print_usage()
{
    echo "Invalid queue manager invocation."
    echo "    Usage: $0 CourseID"
}

errmsg()
{
    echo "QUEUE_MANAGER Error: $1"
}

infomsg()
{
    echo $1
}

# creates a semaphore if one does not already exists
initialize_semaphore()
{
    # only redirect stdout; stderr should still return any encountered errors.
    $semctl exists $course_id > /dev/null
    if [ $? -ne 0 ]; then
        $semctl create $course_id
        if [ $? -ne 0 ]; then
            errmsg "Could not create a semaphore for course: $course_id"
            return 1
        fi
    fi
    return 0
}

wait_on_semaphore()
{
    $semctl down $course_id
}

loop_func()
{
    # wait until notified by the notifier, find the oldest file and process it
    wait_on_semaphore
    if [ $? -ne 0 ]; then
        errmsg "wait_on_semaphore failed. stopping $0"
        exit 1
    fi

    # "ls -ctr"  sorts by creation time (-ct) in reverse (-r) order
    # "ls -1" formats the output in "single column" - one dir entry per line
    # "head -n 1" extract the first line: the name of the oldest file.
    local entry=`ls -ctr1 $hwconf_queue_dir/*.ini 2> /dev/null | head -n 1`

    if [ -n "$entry" ]; then
        echo "a new entry in queue: $entry"
        process_dir_entry "$entry"
    fi

    return $?
}

process_dir_entry()
{
    local entry=$1

    # let's check if it's a valid file
    if [ -f "$entry" ]; then
        invoke_commander "$entry"
        return $?
    else
        errmsg "\"$entry\" should be a filename, but it's not."
        return 0
    fi
}

process_dir_at_startup()
{
    # invoke the commander on all queued entryes.
    for entry in "$hwconf_queue_dir"/*; do
        # if there's noting in the directory just bail out
        if [ "$entry" = "$hwconf_queue_dir/*" ]; then
            infomsg "Clean startup: No entries in $hwconf_queue_dir/"
            return 0
        fi

        # process a posibly valid entry
        process_dir_entry "$entry"
        if [ $? -ne 0 ]; then
            # do not stop after error; there are other homeworks that
            # need checking. Just log the error:
            errmsg "process_dir_entry($entry) failed"
        fi
    done
}

invoke_commander()
{
    local entry=$1
    $commander "$entry"
    if [ $? -ne 0 ]; then
	exit 1
        errmsg "invoke_commander($entry) failed\n"
        errmsg   "    retouching file for later invocation"
        touch "$entry"
        errmsg   "    sleeping for 5 seconds so we don't overload the server"
        sleep 5
        $notifier $course_id
        return 1
    else
        infomsg "Commander returned successfuly for $entry. Unqueued homework."
        rm "$entry"
    fi
    return 0
}

check_executable()
{
	if ! [ -f "$1" ]; then
		errmsg "cannot invoke $1. file doesn't exist"
		exit 1
	fi

	if ! [ -x "$1" ]; then
		errmsg "cannot invoke $1. file it's not executable"
		exit 1
	fi
}


sanity_checks()
{
    if [ -z "$VMCHECKER_ROOT" ]; then
        errmsg "Environment variable VMCHECKER_ROOT is not set."
        exit 1
    fi

    # check if $hwconf_queue_dir/ is actually a directory or not.
    if [ -d "$hwconf_queue_dir/" ]; then
        check_executable $semctl
        check_executable $commander
        check_executable $notifier
    else
        errmsg "main queue $hwconf_queue_dir/ is not a directory."
        exit 1
    fi
}

main()
{
    # init_queue
    process_dir_at_startup
    while true; do
        loop_func
    done
}


if [ -z "$1" ]; then
    print_usage
    exit 1
fi



sanity_checks
initialize_semaphore
if [ $? -ne 0 ]; then
    errmsg "failed while initializing semctl semaphore $course_id"
    exit 1
fi

echo "started $0 on $hwconf_queue_dir for course $course_id"

main
