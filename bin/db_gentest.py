
__author__ = 'Gheorghe Claudiu-Dan, claudiugh@gmail.com'

""" The script generates a test tree for checked homeworks """

import os

NO_OF_HWS = 10
NO_OF_STUDENTS = 100
GRADE = 10
GRADE_FILENAME = 'NOTA'

cwd = os.getcwd()
root = os.path.join(cwd, 'checked')
if not os.path.exists(root):
    print "`checked` directory does not exist in the cwd "
    exit()

for hw_index in range(0,NO_OF_HWS):
    # generate homework dentries
    hw_dir = os.path.join(root, "tema_%d" % hw_index)
    if not os.path.exists(hw_dir):
        os.mkdir(hw_dir)
    for st_index in range(0, NO_OF_STUDENTS):
        # generate student dentries 
        st_dir = os.path.join(hw_dir, "student_%d" % st_index)
        if not os.path.exists(st_dir):
            os.mkdir(st_dir)
        grade_filename = os.path.join(st_dir, GRADE_FILENAME)
        if not os.path.exists(grade_filename):
            # create the grade file 
            f = open(grade_filename, 'w')
            f.write(str(GRADE))
            f.close()

print "Done."
