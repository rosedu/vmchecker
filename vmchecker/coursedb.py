#!/usr/bin/env python

"""Manage the course database"""

from __future__ import with_statement

import sqlite3
from contextlib import contextmanager, closing



class CourseDb(object):
    """A class to encapsulate the logic behind updates and querries of
    the course's db"""

    def __init__(self, db_cursor):
        self.db_cursor = db_cursor

    def create_tables(self):
        """Create the tables needed for vmchecker"""
        self.db_cursor.executescript("""
             CREATE TABLE assignments (id   INTEGER PRIMARY KEY,
                                       name TEXT);

             CREATE TABLE users (id   INTEGER PRIMARY KEY,
                                 name TEXT);

             CREATE TABLE teams (id             INTEGER PRIMARY KEY,
                                 name           TEXT,
                                 mutual_account BOOLEAN);

             CREATE TABLE team_members (team_id       INTEGER,
                                        user_id       INTEGER,
                                        PRIMARY KEY(team_id, user_id));

             CREATE TABLE team_assignments (team_id       INTEGER,
                                            assignment_id INTEGER,
                                            PRIMARY KEY(team_id, assignment_id));

             CREATE TABLE student_grades (assignment_id INTEGER,
                                          user_id       INTEGER,
                                          grade         TEXT,
                                          mtime         TIMESTAMP NOT NULL,
                                          PRIMARY KEY(assignment_id, user_id));

             CREATE TABLE team_grades (assignment_id INTEGER,
                                       team_id       INTEGER,
                                       grade         TEXT,
                                       mtime         TIMESTAMP NOT NULL,
                                       PRIMARY KEY(assignment_id, team_id));""")




    def add_assignment(self, assignment):
        """Creates an id of the homework and returns it."""
        self.db_cursor.execute('INSERT INTO assignments (name) values (?)',
                               (assignment,))
        self.db_cursor.execute('SELECT last_insert_rowid()')
        assignment_id, = self.db_cursor.fetchone()
        return assignment_id

    def get_assignment_id(self, assignment):
        """Returns the id of the assignment."""
        self.db_cursor.execute('SELECT id FROM assignments WHERE name=?',
                               (assignment,))
        result = self.db_cursor.fetchone()
        if result is None:
            return self.add_assignment(assignment)
        return result[0]


    def add_team(self, team, mutual_account):
        """Creates an id of the team and returns it."""
        self.db_cursor.execute('INSERT INTO teams (name, mutual_account) values (?, ?)',
                               (team, mutual_account))
        self.db_cursor.execute('SELECT last_insert_rowid()')
        team_id, = self.db_cursor.fetchone()
        return team_id

    def remove_team(self, team):
        """Removes an existing team."""
        self.db_cursor.execute('DELETE FROM teams '
                               'WHERE teams.name = ? ',
                               (team,))
        return self.db_cursor.rowcount == 1

    def get_team_id(self, team):
        """Returns the id of the team."""
        self.db_cursor.execute('SELECT id FROM teams WHERE name=?',
                               (team,))
        result = self.db_cursor.fetchone()
        if result is None:
            return None
        return result[0]

    def get_team_has_mutual_account(self, team):
        """Returns whether a team has a mutual account or not."""
        self.db_cursor.execute('SELECT mutual_account FROM teams WHERE name=?',
                               (team,))
        result = self.db_cursor.fetchone()
        if result is None:
            return None
        return False if result[0] == 0 else True

    def get_teams(self):
        """Returns a list of existing teams."""
        self.db_cursor.execute('SELECT name, mutual_account FROM teams;')

        return self.db_cursor.fetchall()

    def get_user_teams(self, user):
        """Returns a list of teams for a certain user."""
        self.db_cursor.execute('SELECT teams.name, teams.mutual_account FROM teams '
                               'JOIN team_members ON teams.id = team_members.team_id '
                               'JOIN users ON users.id = team_members.user_id '
                               'WHERE users.name = ?;', (user,))

        return self.db_cursor.fetchall()

    def get_team_assignments(self, team):
        """Returns a list of assignments that the team is active for."""
        self.db_cursor.execute('SELECT assignments.name FROM assignments '
                               'JOIN team_assignments ON assignments.id = team_assignments.assignment_id '
                               'JOIN teams ON teams.id = team_assignments.team_id '
                               'WHERE teams.name = ?;', (team,))

        return self.db_cursor.fetchall()


    def get_user_team_for_assignment(self, assignment, user):
        """Returns the name of the team that a user belongs to for a certain assignment.
        XXX: The DB can support assigning a user to multiple teams for the
        same assignment. However, we assume that a user is only assigned
        to at most one team per assignment."""
        self.db_cursor.execute('SELECT teams.name from teams '
                               'JOIN team_assignments ON team_assignments.team_id = teams.id '
                               'JOIN assignments ON team_assignments.assignment_id = assignments.id '
                               'JOIN team_members ON team_members.team_id = teams.id '
                               'JOIN users ON team_members.user_id = users.id '
                               'WHERE assignments.name = "' + assignment + '" '
                               'AND users.name = "' + user +'";')

        result = self.db_cursor.fetchone()
        if result is None:
            return None
        return result[0]


    def add_team_member(self, user_id, team_id):
        """Add a user to a team."""
        self.db_cursor.execute('INSERT OR IGNORE INTO team_members '
                               '(user_id, team_id) '
                               'VALUES (?, ?) ',
                               (user_id, team_id))

    def remove_team_member(self, user_id, team_id):
        """Remove a user from a team."""
        self.db_cursor.execute('DELETE FROM team_members '
                               'WHERE team_id = ? '
                               'AND user_id = ? ',
                               (team_id, user_id))

        return self.db_cursor.rowcount == 1

    def get_team_members(self, team_id):
        """Return all the members of a team."""
        self.db_cursor.execute('SELECT users.name FROM users '
                               'JOIN team_members ON team_members.user_id = users.id '
                               'WHERE team_members.team_id = ? ;',
                               (team_id,))

        return self.db_cursor.fetchall()

    def activate_team_for_assignment(self, team_id, assignment_id):
        """Make a team active for an assignment."""
        self.db_cursor.execute('INSERT OR IGNORE INTO team_assignments '
                               '(team_id, assignment_id) '
                               'VALUES (?, ?) ',
                               (team_id, assignment_id))

    def deactivate_team_for_assignment(self, team_id, assignment_id):
        """Make a team inactive for an assignment."""
        self.db_cursor.execute('DELETE FROM team_assignments '
                               'WHERE team_id = ? '
                               'AND assignment_id = ? ',
                               (team_id, assignment_id))

        return self.db_cursor.rowcount == 1



    def add_user(self, user):
        """Creates an id of the user and returns it."""
        self.db_cursor.execute('INSERT INTO users (name) values (?)', (user,))
        self.db_cursor.execute('SELECT last_insert_rowid()')
        user_id, = self.db_cursor.fetchone()
        return user_id

    def get_user_id(self, user):
        """Returns the id of the user"""
        self.db_cursor.execute('SELECT id FROM users WHERE name=?', (user,))
        result = self.db_cursor.fetchone()
        if result is None:
            return self.add_user(user)
        return result[0]


    def get_grade_mtime(self, assignment_id, user_id = None, team_id = None):
        """Returns the mtime of a grade"""
        if user_id != None:
            self.db_cursor.execute('SELECT mtime FROM student_grades '
                                   'WHERE assignment_id = ? and user_id = ?',
                                   (assignment_id, user_id))
        elif team_id != None:
            self.db_cursor.execute('SELECT mtime FROM team_grades '
                                   'WHERE assignment_id = ? and team_id = ?',
                                   (assignment_id, team_id))
        else:
            return None

        result = self.db_cursor.fetchone()
        if result is not None:
            return result[0]


    def save_user_grade(self, assignment_id, user_id, grade, mtime):
        """Save a grade for a user into the database.

        If the grade identified by (assignment_id, user_id)
        exists then update the DB, else inserts a new entry.

        """
        self.db_cursor.execute('INSERT OR REPLACE INTO student_grades '
                               '(grade, mtime, assignment_id, user_id) '
                               'VALUES (?, ?, ?, ?) ',
                               (grade, mtime, assignment_id, user_id))

    def save_team_grade(self, assignment_id, team_id, grade, mtime):
        """Save a grade for a team into the database.
        This only makes sense if the team has a mutual account.

        If the grade identified by (assignment_id, team_id)
        exists then update the DB, else inserts a new entry.

        """
        self.db_cursor.execute('INSERT OR REPLACE INTO team_grades '
                               '(grade, mtime, assignment_id, team_id) '
                               'VALUES (?, ?, ?, ?) ',
                               (grade, mtime, assignment_id, team_id))



    def get_user_grades(self, user = None):
        """Return all the individual grades of one or all users."""
        self.db_cursor.execute('SELECT users.name, assignments.name, student_grades.grade ' +
                               'FROM users, assignments, student_grades ' +
                               'WHERE 1 ' +
                               'AND users.id = student_grades.user_id ' +
                               'AND assignments.id = student_grades.assignment_id ' +
                               ('AND users.name = "' + user + '"' if user != None else ''))
        return self.db_cursor.fetchall()

    def get_team_grades(self, team = None):
        """Return the mutual grades of one or all teams."""
        self.db_cursor.execute('SELECT teams.name, assignments.name, team_grades.grade ' +
                               'FROM teams, assignments, team_grades ' +
                               'WHERE 1 ' +
                               'AND teams.id = team_grades.team_id ' +
                               'AND assignments.id = team_grades.assignment_id ' +
                               ('AND teams.name = "' + team + '"' if team != None else ''))
        return self.db_cursor.fetchall()

    def get_user_team_grades(self, user):
        """Return the mutual grades of all the teams that the user is a part of."""
        self.db_cursor.execute('SELECT teams.name, assignments.name, team_grades.grade '
                               'FROM teams, assignments, team_grades '
                               'WHERE 1 '
                               'AND teams.id = team_grades.team_id '
                               'AND teams.mutual_account = 1 '
                               'AND assignments.id = team_grades.assignment_id '
                               'AND teams.id IN '
                               '(SELECT team_members.team_id FROM team_members, users '
                                'WHERE users.id = team_members.user_id '
                                'AND users.name="' + user +'") ')
        return self.db_cursor.fetchall()



    def get_user_and_teammates_grades(self, user):
        """Return all the individual grades that a user should
           always be allowed to see: his own grades and the
           grades of his teammates.

           Note:
            - a user can belong to different teams across different assignments.
            - if a team has a mutual account, then there's no point displaying
            the individual grades for that team."""

        # XXX: This is a highly convoluted piece of SQL. If anybody knows a better
        # way to do this, please change it!
        self.db_cursor.execute('SELECT users.name, assignments.name, student_grades.grade '
                               'FROM users, assignments, student_grades '
                               'JOIN team_members ON team_members.user_id = users.id '
                               'JOIN teams ON teams.id = team_members.team_id '
                               'AND teams.mutual_account = 0 '
                               'JOIN team_assignments ON team_assignments.team_id = team_members.team_id '
                               'AND team_assignments.assignment_id = student_grades.assignment_id '
                               'WHERE users.id = student_grades.user_id '
                               'AND student_grades.assignment_id = assignments.id '
                               'AND team_members.team_id IN '
                               '(SELECT team_members.team_id FROM team_members, users '
                                'JOIN teams ON teams.id = team_members.team_id '
                                'AND teams.mutual_account = 0 '
                                'WHERE users.id = team_members.user_id '
                                'AND users.name="' + user +'") '
                               'UNION '
                               'SELECT users.name, assignments.name, student_grades.grade '
                               'FROM users, assignments, student_grades '
                               'WHERE users.id = student_grades.user_id '
                               'AND assignments.id = student_grades.assignment_id '
                               'AND users.name = "' + user +'";')
        return self.db_cursor.fetchall()



@contextmanager
def opening_course_db(db_file, isolation_level=None):
    """Context manager ensuring that the database resources are
    propperly closed upon either success or exception.

    On success the latest changes must be commited, while on failure
    they must be rolled back.

    """
    db_conn = sqlite3.connect(db_file, isolation_level=isolation_level)
    try:
        with closing(db_conn.cursor()) as db_cursor:
            course_db = CourseDb(db_cursor)
            yield course_db
    except:
        db_conn.rollback()
        raise
    else:
        db_conn.commit()
    finally:
        db_conn.close()


def create_db_tables(db_file):
    """Create vmchecker's tables inside the given db_file"""
    with opening_course_db(db_file) as course_db:
        course_db.create_tables()
