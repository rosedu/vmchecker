#!/bin/bash
# Queue Manager
# Lucian Adrian Grijincu (lucian.grijincu@gmail.com)

# the directory where the homework config files are stored.
hwconf_queue_dir=$1

# the id of the course. It's used to identify the semaphore.
course_id=$2

# path to the commander (gets tests.zip & file.zip and runs the vmexecutor)
commander=`dirname $0`/commander.sh

# path to the IPC semaphore manipulator
semctl=`dirname $0`/semctl

notifier=`dirname $0`/notify.sh


print_usage()
{
    echo "Invalid queue manager invocation."
    echo "    Usage: $0 HW_Queue_dir CourseID"
}

errmsg()
{
    echo "QUEUE_MANAGER Error: $1"
}

infomsg()
{
    echo $1
}

create_semaphore()
{
    $semctl create $course_id
}

wait_on_semaphore()
{
    $semctl down $course_id
}

init_queue()
{
    create_semaphore
    if [ $? -ne 0 ]; then
        errmsg "Could not create IPC for course " $course_id
        exit 1
    fi
    return 0
}

loop_func()
{
    # wait until notified by the notifier
    wait_on_semaphore

    # "ls -ctr"  sorts by creation time (-ct) in reverse (-r) order
    # "ls -1" formats the output in "single column" - one dir entry per line
    # "head -n 1" extract the first line: the name of the oldest file.
    local entry=`ls -ctr1 $hwconf_queue_dir | head -n 1`

    process_dir_entry "$hwconf_queue_dir/$entry"
    return $?
}

process_dir_entry()
{
    local entry=$1
    # is the entry an empty string?
    echo $entry
    if [ -z $entry ]; then
        errmsg "I got notified I but did not find any files in $hwconf_queue_dir"
        return 0
    else
        # $entry is not an empty string
        # let's check if it's a valid file
        if [ -f "$entry" ]; then
            invoke_commander "$entry"
            return $?
        else
            errmsg "Expected $entry to be a filename, but was wrong"
            return 0
        fi
    fi
}

process_dir_at_startup()
{
    # invoke the commander on all queued entryes.
    for entry in `ls -ctr1 $hwconf_queue_dir/`; do
        process_dir_entry "$hwconf_queue_dir/$entry"
        if [ $? -ne 0 ]; then
            # do not stop after error; there are other homeworks that
            #  still need checking. Just log the error:
            errmsg "process_dir_entry($hwconf_queue_dir/$entry) failed"
        fi
    done
}

invoke_commander()
{
    local entry=$1
    $commander $entry
    if [ $? -ne 0 ]; then
        errmsg "invoke_commander($entry) failed\n"
        errmsg   "    retouching file for later invocation"
        touch $entry
        errmsg   "    sleeping for 5 seconds so we don't overload the server"
        sleep 5
        $notifier $course_id
        return 1
    else
        infomsg "Commander returned successfuly for $entry. Delete homework from queue"
        rm $entry
    fi
    return 0
}

check_executable()
{
	if ! [ -f $1 ]; then
		errmsg "cannot invoke $1. file doesn't exist"
		exit 1
	fi

	if ! [ -x $1 ]; then
		errmsg "cannot invoke $1. file it's not executable"
		exit 1
	fi
}

main()
{
    process_dir_at_startup
    while true; do
        loop_func
    done
}


if [ -z $1 ]; then
    print_usage
    exit 1
fi

if [ -z $2 ]; then
    print_usage
    exit 1
fi

check_executable $semctl
check_executable $commander
check_executable $notifier

main
