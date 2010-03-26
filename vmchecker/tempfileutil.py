"""Temporary files.

This module provides generic, low-level interfaces for creating
temporary files and directories.  The interfaces listed as "safe" just
below can be used without fear of race conditions.

This module is inspired from the tempfile module from the python
standard library and was changed to provide users with the ability to
set mode bits.

"""

__all__ = ["mkstemp", "mkdtemp"]


# Imports.

import os as _os
import errno as _errno
from random import Random as _Random


try:
    import thread as _thread
except ImportError:
    import dummy_thread as _thread
_allocate_lock = _thread.allocate_lock

if hasattr(_os, 'TMP_MAX'):
    TMP_MAX = _os.TMP_MAX
else:
    TMP_MAX = 10000

template = "tmp"

# Internal routines.

_once_lock = _allocate_lock()


class _RandomNameSequence:
    """An instance of _RandomNameSequence generates an endless
    sequence of unpredictable strings which can safely be incorporated
    into file names.  Each string is six characters long.  Multiple
    threads can safely use the same instance at the same time.

    _RandomNameSequence is an iterator."""

    characters = ("abcdefghijklmnopqrstuvwxyz" +
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ" +
                  "0123456789_")

    def __init__(self):
        self.mutex = _allocate_lock()
        self.rng = _Random()
        self.normcase = _os.path.normcase

    def __iter__(self):
        return self

    def __next__(self):
        m = self.mutex
        c = self.characters
        choose = self.rng.choice

        m.acquire()
        try:
            letters = [choose(c) for dummy in "123456"]
        finally:
            m.release()

        return self.normcase(''.join(letters))


_name_sequence = None

def _get_candidate_names():
    """Common setup sequence for all user-callable interfaces."""

    global _name_sequence
    if _name_sequence is None:
        _once_lock.acquire()
        try:
            if _name_sequence is None:
                _name_sequence = _RandomNameSequence()
        finally:
            _once_lock.release()
    return _name_sequence


def _mkstemp_inner(dir, pre, suf, mode):
    """Code common to mkstemp, TemporaryFile, and NamedTemporaryFile."""

    names = _get_candidate_names()

    for seq in range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, pre + name + suf)
        try:
            fd = _os.open(file, _os.O_RDWR | _os.O_CREAT | _os.O_EXCL, mode)
            return (fd, _os.path.abspath(file))
        except OSError, e:
            if e.errno == _errno.EEXIST:
                continue # try again
            raise

    raise IOError(_errno.EEXIST, "No usable temporary file name found")


def mkstemp(suffix="", prefix=template, dir="", mode=0660, text=False):
    """User-callable function to create and return a unique temporary
    file.  The return value is a pair (fd, name) where fd is the
    file descriptor returned by os.open, and name is the filename.

    If 'suffix' is specified, the file name will end with that suffix,
    otherwise there will be no suffix.

    If 'prefix' is specified, the file name will begin with that prefix,
    otherwise a default prefix is used.

    If 'dir' is specified, the file will be created in that directory,
    otherwise the current directory is used.

    If 'text' is specified and true, the file is opened in text
    mode.  Else (the default) the file is opened in binary mode.  On
    some operating systems, this makes no difference.

    The file is readable and writable only by the creating user ID.
    If the operating system uses permission bits to indicate whether a
    file is executable, the file is executable by no one. The file
    descriptor is not inherited by children of this process.

    Caller is responsible for deleting the file when done with it.
    """
    return _mkstemp_inner(dir, prefix, suffix, mode)


def mkdtemp(suffix="", prefix=template, dir="", mode=0770):
    """User-callable function to create and return a unique temporary
    directory.  The return value is the pathname of the directory.

    Arguments are as for mkstemp, except that the 'text' argument is
    not accepted.

    The directory is readable, writable, and searchable only by the
    creating user and group.

    Caller is responsible for deleting the directory when done with it.
    """

    names = _get_candidate_names()

    for seq in range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, prefix + name + suffix)
        try:
            _os.mkdir(file, mode)
            return file
        except OSError, e:
            if e.errno == _errno.EEXIST:
                continue # try again
            raise

    raise IOError(_errno.EEXIST, "No usable temporary directory name found")

