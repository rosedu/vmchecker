"""Provides the functionality to work with the vmchecker database"""

from sqlalchemy import create_engine, MetaData, Table


db = None
connection = None

courses = None
assignments = None
holidays = None
users = None
teachers = None
assistants = None
submissions = None
comments = None


def connect(url):
    """Connects to a sql database.

    The url looks like:
        mysql://root:alfabet@localhost/vmchecker

    For more information see:
        sqlalchemy.engine.url.URL
    or
        sqlalchemy.create_engine
    or
        http://www.sqlalchemy.org/docs/05/reference/sqlalchemy/connections.html

    """
    global db, connection
    global courses, assignments, holidays, users
    global teachers, assistants, submissions, comments

    db = create_engine(url)
    connection = db.connect()

    metadata = MetaData()
    metadata.bind = db

    courses = Table('courses', metadata, autoload = True)
    assignments = Table('assignments', metadata, autoload = True)
    holidays = Table('holidays', metadata, autoload = True)
    users = Table('users', metadata, autoload = True)
    teachers = Table('teachers', metadata, autoload = True)
    assistants = Table('assistants', metadata, autoload = True)
    submissions = Table('submissions', metadata, autoload = True)
    comments = Table('comments', metadata, autoload = True)


def clear_tables():
    """Clear all tables (for testing purposes)"""
    for table in reversed([courses, assignments, holidays, users,
            teachers, assistants, submissions, comments]):
        table.delete().execute()
