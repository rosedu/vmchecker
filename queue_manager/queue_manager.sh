#!/bin/sh
# Queue Manager
# Lucian Adrian Grijincu (lucian.grijincu@gmail.com)

# the directory where the homework config files are stored.
hwconf_queue_dir=$1

# the id of the course. It's used to identify the semaphore.
course_id=$2

# path to the commander (gets tests.zip & file.zip and runs the vmexecutor)
commander_binary=./commander

# path to the IPC semaphore manipulator
semctl=../semctl/semctl

notifier=./notify.sh

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
    if [ "$?" != 0 ]; then
        echo "Could not create IPC for course " $course_id
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
    entry = `ls -ctr1 $hwconf_queue_dir | head -n 1`

    process_dir_entry $entry
    return $?
}

process_dir_entry()
{
    entry = $2;
    # is the entry an empty string?
    if [ "$hwconf_queue_dir/$entry" = "$hwconf_queue_dir/" ]; then
        echo "I got notified I but did not find any files in $hwconf_queue_dir"
        return 0;
    else
        # $entry is not an empty string
        # let's check if it's a valid file
        if [ -f "$hwconf_queue_dir/$entry" ]; then
            invoke_commander "$hwconf_queue_dir/$entry"
            return $?
        else
            echo "Expected [[$entry]] to be a filename, but was wrong"
            return 0;
        fi
    fi
}

process_dir_at_startup()
{
    # invoke the commander on all queued entryes.
    for entry in `ls -ctr1 $hwconf_queue_dir/`; do
        process_dir_entry "$hwconf_queue_dir/$entry"
        if [ "$?" != 0 ]; then
            # do not stop after error; there are other homeworks that
            #  still need checking. Just log the error:
            echo "process_dir_entry($hwconf_queue_dir/$entry) failed"
        fi
    done
}

invoke_commander()
{
    entry = $1
    commander $entry
    if [ "$?" == 0 ]; then
        echo "invoke_commander($entry) failed"
        echo "  retouching file for later invocation"
        echo "  sleeping for 5 seconds so we don't overload the server"
        touch $entry
        sleep 5
        notifier $course_id
        return 1
    fi
    return 0
}


main()
{
    process_dir_at_startup
    while true; do
        loop_func
    done
}


main
