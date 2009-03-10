#! /usr/bin/env python

import dircache
import misc
import optparse
import os
import submit
import sys
import traceback

from os.path import join


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-u', '--user', action='append',
                      help='user (omit for all users')
    parser.add_option('-a', '--assignment', action='append',
                      help='assignment (omit for all assignments)')
    (options, args) = parser.parse_args()

    users = options.user
    assignments = options.assignment

    if assignments is None:
        print >>sys.stderr, 'No assigment specified. Assuming all.'
        assignments = misc.config().sections()

    if users is None:
        print >>sys.stderr, 'No user specfied. Assuming all.'

    counter = 0
    for a in assignments:
        if not a in misc.config().sections():
            print >>sys.stderr, 'Unknown assignment `%s\'. Ignoring.' % a
            continue

        repository = join(misc.repository(a), a)

        users_ = users
        if users_ is None:
            users_ = dircache.listdir(repository)

        for u in users_:
            # gets user's homework directory
            location = join(repository, u)
            if not os.path.isdir(location):
                print >>sys.stderr, 'Not a directory `%s\'. Ignoring.' % location
                continue

            # gets configuration file
            location = join(location, 'config')
            if not os.path.isfile(location):
                print >>sys.stderr, 'Not a file `%s\'. Ignoring.' % location
                continue

            print '++++ Assignment `%s\'; User `%s\' ++++' % (a, u)
            print 'Submiting `%s\'' % location

            try:
                submit.submit_assignment(location)
            except Exception:
                traceback.print_exc()

            print
            counter += 1

    print 'Resubmitted %d homework(s)' % counter
