#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple in-house directory locking based on file locking."""


import os
import fcntl


class DirLock(object):
    """Provides a directory lock over, with an interface simmilar to
    threading.Lock.
    
    It creates a temporary '.lock' file in the locked directory and
    deletes it upon object destruction.

    """
    def __init__(self, directory_to_lock):
        if not os.path.isdir(directory_to_lock):
            os.makedirs(directory_to_lock)

        self.__fd = os.open(
                os.path.join(directory_to_lock, '.lock'),
                os.O_CREAT | os.O_RDWR, 0660)
        assert self.__fd != -1

    def acquire(self):
        """Exclusively acquires the lock"""
        fcntl.lockf(self.__fd, fcntl.LOCK_EX)

    def __enter__(self):
        self.acquire()

    def release(self):
        """Releases the lock"""
        fcntl.lockf(self.__fd, fcntl.LOCK_UN)

    def __exit__(self, type_, value, traceback):
        self.release()

    def __del__(self):
        os.close(self.__fd)







