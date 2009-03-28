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


import sys
import tempfile
import shutil
import misc
import vmcheckerpaths
import logging
import os
import time

from subprocess import check_call
from os.path import join
from pyinotify import WatchManager, Notifier, ProcessEvent, EventsCodes


__author__ = """Alexandru Moșoi <brtzsnr@gmail.com>,
                Lucian Adrian Grijincu <lucian.grijincu@gmail.com>"""


_logger = logging.getLogger("vmchecker.queue_manager")

class _QueueManager(ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        process_job(event.path, event.name)



def process_job(path, name):
    """Unzip a job archive and call the commander"""
    location = tempfile.mkdtemp(prefix='vmchecker-',
                                dir=vmcheckerpaths.dir_tester_unzip_tmp())
    archive = join(path, name)
    try:
        _logger.info('Expanding archive `%s\' at `%s\'.' % (archive, location))
        check_call(['unzip', '-d', location, archive])

        _logger.info('Calling commander for [%s]' % location)
        commander_path = join(vmcheckerpaths.dir_bin(), 'commander.py')
        check_call([commander_path, location])
    except:
        _logger.exception('Caught exception while processing [%s]' % location)
    finally:
        _logger.info('Cleaning [%s]' % location)
        shutil.rmtree(location)



def process_stale_jobs(dir_queue):
    """The queue_manager may die leaving jobs unchecked.
    This function runs the commander for each"""
    stale_jobs = os.listdir(dir_queue)
    if len(stale_jobs) == 0:
        _logger.info('No stale jobs in queue dir [%s]' % dir_queue)
    for stale_job in stale_jobs:
        _logger.info('Processing stale job [%s] in queue dir %s' % (
                stale_job, dir_queue))
        process_job(dir_queue, stale_job)



def start_queue():
    dir_queue = vmcheckerpaths.dir_queue()
    if not os.path.isdir(dir_queue):
        _logger.error('Queue direcotry [%s] missing')
        exit(1)

    # register for inotify envents before processing stale jobs
    wm = WatchManager()
    notifier = Notifier(wm, _QueueManager())
    wm.add_watch(dir_queue, EventsCodes.ALL_FLAGS['IN_CLOSE_WRITE'])

    process_stale_jobs(dir_queue)

    # set callback to receive notifications
    notifier.loop(callback=lambda self: self.proc_fun())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    start_queue()

