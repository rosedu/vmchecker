#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Queue manager - wait for assignments and invoke the commander for each

This module depends on pyinotify: http://pyinotify.sourceforge.net/
It should:
  * listen for new files on a directory,
  * decompress the archives to a temporary directory,
  * pass path of the directory to commander,
  * waits for the commander to finish.

Note, the last two steps must be grouped together: queue_manager should
call a script ./callback located in archive which does this shit.

"""

import tempfile
import shutil
import logging
import os
import subprocess
from pyinotify import WatchManager, Notifier, ProcessEvent, EventsCodes

import vmcheckerpaths


_logger = logging.getLogger("vmchecker.queue_manager")


class _InotifyHandler(ProcessEvent):
    """Dummy class needed to start processing events"""
    def process_IN_CLOSE_WRITE(self, event):
        """Called when a write ends (this means a new
        archive has arrived). Imediatly start the new job.

        """
        process_job(event.path, event.name)


def process_job(path, name):
    """Unzip a job archive and call the commander."""
    location = tempfile.mkdtemp(prefix='vmchecker-',
                                dir=vmcheckerpaths.dir_tester_unzip_tmp())
    archive = os.path.join(path, name)
    try:
        _logger.info('Expanding archive "%s" at "%s".' % (archive, location))
        subprocess.check_call(['unzip', '-d', location, archive])

        _logger.info('Calling commander for "%s"' % location)
        commander_path = os.path.join(vmcheckerpaths.dir_bin(), 'commander.py')

        subprocess.check_call([commander_path, location])
    except subprocess.CalledProcessError:
        _logger.exception('Failed to process "%s".' % location)

    _logger.info('Cleaning "%s"' % location)
    shutil.rmtree(location)

    _logger.info('Removing job from the queue')
    os.unlink(archive)


def process_stale_jobs(dir_queue):
    """The queue_manager may die leaving jobs unchecked.
    This function runs the commander for each job found
    in the queue directory at startup.

    """
    stale_jobs = os.listdir(dir_queue)
    if len(stale_jobs) == 0:
        _logger.info('No stale jobs in queue dir "%s"' % dir_queue)
    for stale_job in stale_jobs:
        _logger.info('Processing stale job "%s" in queue dir "%s"' % (
                stale_job, dir_queue))
        process_job(dir_queue, stale_job)


def _callback():
    _logger.info('Waiting for the next job to arrive')


def start_queue():
    """ Process any stale jobs and register with inotify to wait
    for new jobs to arrive.

    """
    dir_queue = vmcheckerpaths.dir_queue()

    # register for inotify envents before processing stale jobs
    wm = WatchManager()
    wm.add_watch(dir_queue, EventsCodes.ALL_FLAGS['IN_CLOSE_WRITE'])
    notifier = Notifier(wm, _InotifyHandler())

    process_stale_jobs(dir_queue)

    # set callback to receive notifications (includes queued jobs after
    # setting up inotify but before we finished processing stale jobs)
    notifier.loop(callback=_callback)


def check_tester_setup_correctly():
    """ Sanity checks:
        * all needed paths are present
        * there is a VMExecutor/vmexecutor file to run.

    """
    # check needed paths setup correctly
    for path in vmcheckerpaths.tester_paths():
        if not os.path.isdir(path):
            _logger.error('"%s" missing. Run `make tester-dist`!', path)
            exit(1)
    # check binaries build
    # TODO: XXX: Hardcoded
    # VMExecutor is expected to die soon :)
    if not os.path.isfile(os.path.join(vmcheckerpaths.abspath('VMExecutor'),
                                       'vm_executor')):
        _logger.error('VMExecutor/vm_executor missing. Run `make tester-dist`!')
        exit(1)

def main():
    """Entry point for the queue manager."""
    logging.basicConfig(level=logging.DEBUG)
    check_tester_setup_correctly()
    start_queue()

if __name__ == '__main__':
    main()
