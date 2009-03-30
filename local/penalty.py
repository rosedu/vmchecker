#! /usr/bin/env python
"""Computes the penalty for one homework based on days passed after deadline.

Usage:
    ./penalty.py upload_time deadline

Input:
    upload_time = time of upload (string)
    deadline = assignment deadline (string)
    date format: 'YYYY.mm.dd hh:mm:ss'

Output:
    penalty_points = number of points to be substracted from the grade
    days_late = number of days exceeding the deadline"""


__author__='Ana Savu <ana.savu86@gmail.com>, Lucian Adrian Grijincu <lucian.grijincu@gmail.com>'


import sys
import time
import math
import datetime

DATE_FORMAT = '%Y.%m.%d %H:%M:%S'  # XXX must be the same as in bin/misc.py


def compute_penalty(upload_time, deadline, penalty, wheights, limit):
    """A generic function to compute penalty

    Args:
        penalty - for every day after the deadline the product
                  of the penalty and the wheight is added to the
                  penalty_points variable
        wheights - the penalty's wheight per day (the last wheight
                   from the list is used for subsequent computations)
        limit - the limit for the penalty value
    Returns:
        Number of penalty points.

    Note: time interval between deadline and upload time (seconds)
    is time.mktime(upload_time) - time.mktime(deadline)"""

    penalty_points = 0

    interval = time.mktime(upload_time) - time.mktime(deadline)
    # only if the number of days late is positive (deadline exceeded)
    if interval > 0:
        days_late = int(math.ceil(interval / (3600 * 24)))

        for i in range(days_late):
            # the penalty exceeded the limit
            if penalty_points > limit:
                break
            else:
                # for every day late the specific wheight is used
                wheight = wheights[min(i, len(wheights) - 1)]
                penalty_points += wheight * penalty
    else:
        days_late = 0

    return (min(penalty_points, limit), days_late)


# common examples of `compute_penalty'. use any of your choice
def compute_penalty_fixed_penalty(upload_time, deadline):
    # if the number of days past the deadline exceeds 'x' the homework is
    # not graded (x = len(wheights) - 1)
    return compute_penalty(upload_time, deadline, 1, [2, 0, 0, 0, 0, 0, 0, 9], 10)


def compute_penalty_linear(upload_time, deadline):
    # for every day past the deadline the penalty value is added
    # to the penalty_points
    return compute_penalty(upload_time, deadline, 0.25, [1], 3)


def compute_penalty_fixed_deadline(upload_time, deadline):
    # if the number of days past the deadline exceeds 'x' the homework is
    # not graded (x = len(wheights) - 1)
    return compute_penalty(upload_time, deadline, 1, [1, 1, 1, 7], 10)


def compute_penalty_wheighted(upload_time, deadline):
    # the wheight for penalty is diferent depending on the day
    return compute_penalty(upload_time, deadline, 1, [1, 2, 3, 4, 0], 10)


def verbose_time_difference(upload_time, deadline):
    interval = time.mktime(upload_time) - time.mktime(deadline)
    penalty_points = 0

    if interval < 0:
        str = 'inainte de termenul limita cu'
        interval = - interval
    else:
        str = 'dupa termenul limita cu'

    d = datetime.timedelta(seconds=interval)
    return str + ' %d zile %d ore %d minute %d secunde' % (
            d.days, d.seconds / 3600, d.seconds % 3600 / 60, d.seconds % 60)


def main():
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage:\n\t%s upload_time deadline' % sys.argv[0]
        sys.exit(1)

    upload_time = time.strptime(sys.argv[1], DATE_FORMAT)
    deadline = time.strptime(sys.argv[2], DATE_FORMAT)

    # ++++ MODIFY NEXT LINE + MODIFY NEXT LINE + MODIFY NEXT LINE ++++
    penalty_points, days_late = compute_penalty_fixed_penalty(upload_time, deadline)

    # prints penalty and number of days late
    print '-%.2f: %s' % (penalty_points, verbose_time_difference(upload_time, deadline))


if __name__ == '__main__':
    main()
