#! /usr/bin/env python2.5
# Penalty
#
# Computes the penalty for one homework based on a predefined value and a 
# wheight list
#
# Usage:
#   ./penalty.py upload_time deadline
#
# Input:
#   upload_time = time of upload (string)
#   deadline = assignment deadline (string)
#       date format: "dd-mm-yy hh:mm:ss"
# Output:
#   penalty_points = number of points to be substracted from the grade
#   days_late = number of days exceeding the deadline


__author__='Ana Savu <ana.savu86@gmail.com>, Lucian Adrian Grijincu <lucian.grijincu@gmail.com>'


import sys
import time
import math
import datetime


def parse_time(upload_time_str, deadline_str):
    # parse input strngs according to format
    upload_time = time.strptime(upload_time_str, "%d-%m-%y %H:%M:%S")
    deadline = time.strptime(deadline_str, "%d-%m-%y %H:%M:%S")

    return (upload_time, deadline)


def compute_penalty(upload_time, deadline, penalty, wheights, limit):
    # penalty - for every day after the deadline the product of the penalty and 
    #   the wheight is added to the penalty_points variable
    # wheights - the penalty's wheight per day (the last wheight from the list 
    # is used for subsequent computations)
    # limit - the limit for the penalty value

    # time interval between deadline and upload time (seconds)
    interval = time.mktime(upload_time) - time.mktime(deadline)

    penalty_points = 0

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



def compute_penalty_fixed_penalty(upload_time, deadline):
    # if the number of days pass the deadline exceeds 'x' the homework is
    # not graded (x = len(wheights) - 1)
    return compute_penalty(upload_time, deadline, 1, [2, 0, 0, 0, 0, 0, 0, 9], 10)


def compute_penalty_linear(upload_time, deadline):
    # for every day pass the deafline the penalty value is added
    # to the penalty_points
    return compute_penalty(upload_time, deadline, 0.25, [1], 3)


def compute_penalty_fixed_deadline(upload_time, deadline):
    # if the number of days pass the deadline exceeds 'x' the homework is
    # not graded (x = len(wheights) - 1)
    return compute_penalty(upload_time, deadline, 1, [1, 1, 1, 7], 10)


def compute_penalty_wheighted(upload_time, deadline):
    # the wheight for penalty is diferent depending on the day
    return compute_penalty(upload_time, deadline, 1, [1, 2, 3, 4, 0], 10)


def verbose_time_difference(upload_time, deadline):
    interval = time.mktime(upload_time) - time.mktime(deadline)
    penalty_points = 0

    if interval < 0:
        str = "inainte de deadline cu "
        interval = - interval
    else:
        str = "intarziat "

    d = datetime.timedelta(seconds=interval)
    return str + " %d zile %d ore %d minute %d secunde" % (d.days,
                                                           d.seconds / 3600,
                                                           d.seconds % 3600 /60,
                                                           d.seconds % 60)

        
    
def main():
   
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Usage: %s upload_time deadline' % sys.argv[0]
        sys.exit(1)
    
    upload_time_str = sys.argv[1]
    deadline_str = sys.argv[2]

    (upload_time, deadline) = parse_time(upload_time_str, deadline_str)

    # based on the type of penalty computing used call one of 
    # the functions below
    # (penalty_points, days_late) = compute_penalty_linear(upload_time, deadline)
    # (penalty_points, days_late) = compute_penalty_fixed_deadline(upload_time, deadline)
    (penalty_points, days_late) = compute_penalty_fixed_penalty(upload_time, deadline)
    # (penalty_points, days_late) = compute_penalty_wheighted(upload_time, deadline)
    # (penalty_points, days_late) = compute_penalty(upload_time, deadline, my_penalty, 
    #         my_wheights, my_limit)

    
    #if penalty_points > 0:
    print "-%.2f: %s" % (penalty_points, verbose_time_difference(upload_time, deadline))
    
if __name__ == '__main__':
    main()
