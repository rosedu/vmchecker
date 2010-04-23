==============================
     vmchecker user guide
==============================

This is a guide for teaching assistants using vmchecker. For information about vmchecker structure, sources and contributing guidelines check HACKING.rst

Course directory structure
==========================
The files in each course's vmchecker-storer directory:

- ``auth_file.json`` - custom accounts for students who cannot use LDAP for authentication
   - entries are of the form ``"username" : "password"``
   - after editing this file check that authentication still works as JSON formatting errors may block the login for all students
- ``config`` - course configuration file (see bellow)
- ``repo`` - a ``git`` repository of all students assignments
   Structure: repo/``assignment-name``/``student-name``/

   - ``archive.zip`` - the student's last submission for this assignment
   - ``archive`` - unzipped version of this submission. The contents of this directory are stored in the ``git`` repository. You can use ``git`` to see previous versions of the student's submissions for this assignment.
   - ``results`` - this is only present if the submission was tested.
      - ``build-stdout.vmr`` ``build-stderr.vmr`` - output of the submission's and test compilation
      - ``run-stdout.vmr`` ``run-stderr.vmr`` - output from running the tests
      - ``run-km.vmr`` - kernel messages (dmesg, dbgview)
      - ``vmchecker-stderr.vmr`` - vmchecker internal errors
      - ``grade.vmr`` - see ``Grading`` section bellow.




Grading
=======

To grade a homework you must edit repo/``assignment-name``/``student-name``/results/grade.vmr.

Penalties for exceeding the deadline will be automatically computed based on the submission's upload time, the assignment's deadline (official holidays are not counted as penalties).

For an unmarked submission, the grade.vmr file contains only one word: "``ok``".

``vmchecker`` reads all lines from grade.vmr and interprets only the first word on the line. If the word is a number (convertible to ``float`` in Python) than that number is added to the total grade (``10`` for a perfect submission).


Examples (considering the submission sent before the deadline)::

   +1.0 nice algorithm
   -0.2: ugly intendation
   It's almost unreadable!
   
   -0.1: inconsitent naming
   0.1: nice README

   graded by: Lucian Adrian Grijincu


The previous example is graded at ``10 + 1.0 - 0.2 - 0.1 = 10.7``. The grade is not bounded by ``10`` because some assignments may have bonuses.

The spacing before the first number on the line is ignored. After the number you may only put whitespace or '``:``'. Anything else and the number is treated as a string and not added to the grade.

As lines that do not begin with a number are ignored by the grading tools, but displayed to the student, you can use this file to comment and argument the penalty/bonuses given. Writing your name in the file will tell the student who to contact if he has any remarks regarding the grading.


*ATENTION* *BUG!*: ``vmchecker`` will DELETE results and ``grade.vmr`` when the student send another submission for that assignment. ``vmchecker`` does not prevent a student from uploading a homework again after it was graded!


Config
======
TODO


Add a new assignment
====================

An example assignment specification::

   [assignment minishell-windows]
   Deadline = 2010.03.31 23:59:00
   Machine = so-win
   Timeout=150
   AssignmentTitle = Minishell (Windows)
   StatementLink = http://elf.cs.pub.ro/so/wiki/teme/tema-1
   OrderNumber = 2

The string after ``assignment`` is the ID of the assignment. This may *NOT* contain spaces!

- ``Deadline`` - the date after which students are penalized for late submissions
- ``Machine``  - the ID of the virtual machine used to test this assignment
- ``Timeout`` is the ammount of time (in seconds) after which testing is aborted.
- ``AssignmentTitle`` - a human readable name for the assignment
- ``StatementLink`` - a link to a resource (pdf, html, etc.) describing the assignment
- ``OrderNumber`` is used to order assignments when presented to the student. These should be numbers starting from ``1`` for the first assignment and incremented for each new one.

Assignment test archives must be placed in tests/``assignment-id``.zip
