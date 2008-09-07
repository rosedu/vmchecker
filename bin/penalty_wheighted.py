#! /usr/bin/python
# Penalty
#
# Calculeaza penalizarea primita de o tema in functie de o valoare predefinita
#
# Utilizare:
#   ./penalty.py nota data_upload deadline
#
# Intrari:
#   grade = nota temei inainte de depunctare
#   upload_time = timpul la care s-a facut upload-ul temei
#   deadline
# Iesire:
#   grade = nota finala dupa depunctare


__author__='Ana Savu, ana.savu86@gmail.com'


import sys
import datetime
import time
import math


# Pentru fiecare zi intarziere se scade valoarea penalty
penalty = 0.25
# Ponderea penalizarii pe zile 
wheights = (1, 2, 4, 8, 0)

def main():
   
    global penalty

    if len(sys.argv) != 4:
        print >> sys.stderr, 'Usage: %s grade upload_time deadline' % sys.argv[0]
        sys.exit(1)
    
    grade = float(sys.argv[1])
    upload_time = sys.argv[2]
    deadline = sys.argv[3]

    # parseaza stringurile primite la intrare conform formatului stabilit
    upload_time = time.strptime(upload_time, "%d %m %y %H:%M:%S")
    deadline = time.strptime(deadline, "%d %m %y %H:%M:%S")

    # intervalul de timp dintre deadline si momentul de upload (in secunde)
    interval = time.mktime(upload_time) - time.mktime(deadline)
    
    # ne intereseaza numai daca numarul de zile este pozitiv (s-a depasit deadline-ul)
    if interval > 0:
        days_late = math.ceil(interval/86400)
        
        for i in range(int(days_late)):
            # pentru fiecare zi intarziere se gaseste ponderea specifica
            wheight = wheights[min (i, len(wheights)-1)]
            grade -= wheight * penalty 

    # nota minima este 0
    return max(grade, 0)

if __name__ == '__main__':
    main()
