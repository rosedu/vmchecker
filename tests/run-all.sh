#!/bin/sh

./setup.py clean && ./setup.py install --home=~

# python ./tests/ut_course.py
# python ./tests/ut_assignments.py
python ./tests/ut_submit.py
