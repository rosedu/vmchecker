#! /usr/bin/python
# Penalty
#
# Calculeaza penalizarea primita de o tema in functie de o valoare predefinita si de o lista de ponderi
#
# Utilizare:
#   ./penalty.py nota data_upload deadline
#
# Intrari:
#   grade = nota temei inainte de depunctare
#   upload_time = timpul la care s-a facut upload-ul temei (string)
#   deadline = deadline-ul temei (string)
#       datele sunt de forma: "dd-mm-yy hh:mm:ss"
# Iesire:
#   grade = nota finala dupa depunctare


__author__='Ana Savu, ana.savu86@gmail.com'


import sys
import time
import math


def parse_time(upload_time_str, deadline_str):

    # parseaza stringurile primite la intrare conform formatului stabilit
    upload_time = time.strptime(upload_time_str, "%d-%m-%y %H:%M:%S")
    deadline = time.strptime(deadline_str, "%d-%m-%y %H:%M:%S")

    return (upload_time, deadline)


def compute_grade(grade, upload_time, deadline, penalty, wheights, limit):

# penalty - pentru fiecare zi intarziere se scade valoarea penalty inmultita cu ponderea pentru ziua respectiva
# wheights - ponderea penalizarii pe zile (ultima pondere din lista se foloseste la calculele urmatoare)
# limit - se penalizeaza pana la maxim 'limit' puncte

    # intervalul de timp dintre deadline si momentul de upload (secunde)
    interval = time.mktime(upload_time) - time.mktime(deadline)

    new_grade = grade

    # ne intereseaza numai daca numarul de zile ese pozitiv (s-a depasit deadline-ul)
    if interval > 0:
        # numar intreg de zile intarziere
        days_late = int(math.ceil(interval / (3600 * 24)))
        
        for i in range(days_late):

            # daca s-a depasit limita de puncte care pot fi scazute calculul se incheie
            if (grade - new_grade) > limit:
                break
            else:
                # pentru fiecare zi intarziere se gaseste ponderea specifica
                wheight = wheights[min(i, len(wheights) - 1)]
                new_grade -= wheight * penalty

    # nota initiala se scade cu maxim 'limit' puncte
    return max(new_grade, grade - limit)


def compute_grade_linear(grade, upload_time, deadline):
    
    # pentru fiecare zi intarziere se scade valoarea 'penalty' (0.25) 
    return compute_grade(grade, upload_time, deadline, 0.25, [1], 3)


def compute_grade_fixed_deadline(grade, upload_time, deadline):

    # dupa 'x' zile de la depasirea deadline-ului tema nu mai este punctata (x = len(wheights) - 1)
    return compute_grade(grade, upload_time, deadline, 1, [1, 1, 1, 7], 10)


def compute_grade_wheighted(grade, upload_time, deadline):

    # ponderea penalizarii creste in functie de zi
    return compute_grade(grade, upload_time, deadline, 1, [1, 2, 3, 4, 0], 10)


def main():
   
    if len(sys.argv) != 4:
        print >> sys.stderr, 'Usage: %s grade upload_time deadline' % sys.argv[0]
        sys.exit(1)
    
    grade = float(sys.argv[1])
    upload_time_str = sys.argv[2]
    deadline_str = sys.argv[3]

    (upload_time, deadline) = parse_time(upload_time_str, deadline_str)

    # in functie de modul de calcul al penalizarii apelati una din functiile urmatoare
    new_grade = compute_grade_linear(grade, upload_time, deadline)
    # new_grade = compute_grade_fixed_deadline(grade, upload_time, deadline)
    # new_grade = compute_grade_wheighted(grade, upload_time, deadline)
    # new_grade = compute_grade(grade, upload_time, deadline, my_penalty, my_wheights, my_limit)

    # nota minima este 0
    print max(new_grade, 0)

if __name__ == '__main__':
    main()
