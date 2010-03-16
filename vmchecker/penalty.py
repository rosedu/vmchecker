#! /usr/bin/env python
# -*- coding: utf-8 -*-
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



import sys
import time
import math
import datetime

from .config import DATE_FORMAT


def str_to_time(time_str, format_str=DATE_FORMAT):
    """Interprets time_str as a time value specified by format_str and
    returns that time object"""
    return time.mktime(time.strptime(time_str, format_str))


def compute_penalty(upload_time, deadline, penalty, weights, limit,
                        holiday_start = None, holiday_finish = None):
    """A generic function to compute penalty

    Args:
        penalty - for every day after the deadline the product
                  of the penalty and the weight is added to the
                  penalty_points variable
        weights - the penalty's weight per day (the last weight
                   from the list is used for subsequent computations)
        limit - the limit for the penalty value
    Returns:
        Number of penalty points.

    Note: time interval between deadline and upload time (seconds)
    is time.mktime(upload_time) - time.mktime(deadline)

    """
    if holiday_start is None:
        holiday_start = []

    if holiday_finish is None:
        holiday_finish = []

    # XXX refactor such that instead of holiday_start and holiday_finish
    # only one list (of intervals) is used

    sec_upload_time = time.mktime(upload_time)
    sec_deadline = time.mktime(deadline)
    interval = sec_upload_time - sec_deadline
    penalty_points = 0

    if interval > 0:
        #compute the interval representing the intersection between
        #(deadline, upload_time) and (holiday_start[i], holiday_finish[i])

        if holiday_start != []:
            for i in range(len(holiday_start)):
                sec_start = str_to_time(holiday_start[i])
                sec_finish = str_to_time(holiday_finish[i])
                maxim = max(sec_start, sec_deadline)
                minim = min(sec_finish, sec_upload_time)
                if minim > maxim:
                    interval -= (minim - maxim)

    # only if the number of days late is positive (deadline exceeded)
    if interval > 0:

        days_late = int(math.ceil(interval / (3600 * 24)))

        for i in range(days_late):
            # the penalty exceeded the limit
            if penalty_points > limit:
                break
            else:
                # for every day late the specific weight is used
                weight = weights[min(i, len(weights) - 1)]
                penalty_points += weight * penalty
    else:
        days_late = 0

    return (min(penalty_points, limit), days_late)


# common examples of `compute_penalty'. use any of your choice
def compute_penalty_fixed_penalty(upload_time, deadline):
    """if the number of days past the deadline exceeds 'x' the homework is
    not graded (x = len(weights) - 1)"""
    return compute_penalty(upload_time, deadline, 1,
                                [2, 0, 0, 0, 0, 0, 0, 9], 10)


def compute_penalty_linear(upload_time, deadline):
    """for every day past the deadline the penalty value is added
    to the penalty_points"""
    return compute_penalty(upload_time, deadline, 0.25, [1], 3)


def compute_penalty_fixed_deadline(upload_time, deadline):
    """if the number of days past the deadline exceeds 'x' the homework is
    not graded (x = len(weights) - 1)"""
    return compute_penalty(upload_time, deadline, 1, [1, 1, 1, 7], 10)


def compute_penalty_weighted(upload_time, deadline):
    """the weight for penalty is diferent depending on the day"""
    return compute_penalty(upload_time, deadline, 1, [1, 2, 3, 4, 0], 10)


def verbose_time_difference(upload_time, deadline):
    """returns an intuitive human-readable representation of the
    difference between two dates"""
    interval = time.mktime(upload_time) - time.mktime(deadline)

    if interval < 0:
        msg = 'tema trimisă inainte de termenul limită cu'
        interval = - interval
    else:
        msg = 'tema trimisă după termenul limită cu'

    diff = datetime.timedelta(seconds = interval)
    return msg + ' %d zile %d ore %d minute %d secunde.\n Tema a fost  \
                  corectată la data %s ' % (diff.days, diff.seconds / 3600,
                  diff.seconds % 3600 / 60, diff.seconds % 60,
                  datetime.datetime.now())


def _test():
    """Test this script with dates taken from the command line"""
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Usage:\n\t%s upload_time deadline' % sys.argv[0]
        sys.exit(1)

    upload_time = time.strptime(sys.argv[1], DATE_FORMAT)
    deadline = time.strptime(sys.argv[2], DATE_FORMAT)

    # ++++ MODIFY NEXT LINE + MODIFY NEXT LINE + MODIFY NEXT LINE ++++
    (penalty_points, _) = compute_penalty_linear(upload_time, deadline)

    # prints penalty and number of days late
    print '-%.2f: %s' % (penalty_points,
                         verbose_time_difference(upload_time, deadline))


if __name__ == '__main__':
    _test()
