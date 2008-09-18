#! /usr/bin/python
# Penalty
#
# Computes the penalty for one homework based on a predefined value and a 
# wheight list
#
# Usage:
#   ./penalty.py grade upload_time deadline
#
# Input:
#   grade = homework grade before recomputing
#   upload_time = time of upload (string)
#   deadline = assignment deadline (string)
#       date format: "dd-mm-yy hh:mm:ss"
# Output:
#   grade = final grade


__author__='Ana Savu, ana.savu86@gmail.com'


import sys
import time
import math


def parse_time(upload_time_str, deadline_str):

    # parse input strngs according to format

    upload_time = time.strptime(upload_time_str, "%d-%m-%y %H:%M:%S")
    deadline = time.strptime(deadline_str, "%d-%m-%y %H:%M:%S")

    return (upload_time, deadline)


def compute_grade(grade, upload_time, deadline, penalty, wheights, limit):

# penalty - for every day after the deadline the product of the penalty and 
#   the wheight is substracted from the grade
# wheights - the penalty's wheight per day (the last wheight from the list 
# is used for subsequent computations)
# limit - the limit for the penalty value

    # time interval between deadline and upload time (seconds)
    interval = time.mktime(upload_time) - time.mktime(deadline)

    new_grade = grade

    # only if the number of days late is positive (deadline exceeded)
    if interval > 0:
        days_late = int(math.ceil(interval / (3600 * 24)))
        
        for i in range(days_late):

            # the penalty exceeded the limit
            if (grade - new_grade) > limit:
                break
            else:
                # for every day late the specific wheight is used
                wheight = wheights[min(i, len(wheights) - 1)]
                new_grade -= wheight * penalty

    return max(new_grade, grade - limit)


def compute_grade_linear(grade, upload_time, deadline):
    
    # for every day pass the deafline the penalty value is substracted 
    # from the grade 
    return compute_grade(grade, upload_time, deadline, 0.25, [1], 3)


def compute_grade_fixed_deadline(grade, upload_time, deadline):

    # if the number of days pass the deadline exceeds 'x' the homework is
    # not graded (x = len(wheights) - 1)
    return compute_grade(grade, upload_time, deadline, 1, [1, 1, 1, 7], 10)


def compute_grade_wheighted(grade, upload_time, deadline):

    # the wheight for penalty is diferent depending on the day
    return compute_grade(grade, upload_time, deadline, 1, [1, 2, 3, 4, 0], 10)


def main():
   
    if len(sys.argv) != 4:
        print >> sys.stderr, 'Usage: %s grade upload_time deadline' % sys.argv[0]
        sys.exit(1)
    
    grade = float(sys.argv[1])
    upload_time_str = sys.argv[2]
    deadline_str = sys.argv[3]

    (upload_time, deadline) = parse_time(upload_time_str, deadline_str)

    # based on the type of penalty computing used call one of 
    # the functions below
    new_grade = compute_grade_linear(grade, upload_time, deadline)
    # new_grade = compute_grade_fixed_deadline(grade, upload_time, deadline)
    # new_grade = compute_grade_wheighted(grade, upload_time, deadline)
    # new_grade = compute_grade(grade, upload_time, deadline, my_penalty, 
    #        my_wheights, my_limit)

    # min grade is 0
    print max(new_grade, 0)

if __name__ == '__main__':
    main()
