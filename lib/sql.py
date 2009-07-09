from sqlalchemy import create_engine, MetaData, Table

engine = create_engine('mysql://root:alfabet@localhost/vmchecker')
engine.echo = False

metadata = MetaData()
metadata.bind = engine

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
    for table in [courses, assignments, holidays, users,
            teachers, assistants, submissions, comments]:
        table.delete().execute()
