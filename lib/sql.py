from sqlalchemy import create_engine, Column, MetaData, Table
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import INT, FLOAT, TIMESTAMP, VARCHAR

metadata = MetaData()

courses = Table('courses', metadata,
        Column('id',            INT),
        Column('name',          VARCHAR,      nullable = False),

        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'))

assignments = Table('assignments', metadata,
        Column('id',            INT),
        Column('course_id',     INT,          nullable = False),
        Column('name',          VARCHAR,      nullable = False),
        Column('url',           VARCHAR),
        Column('repository',    VARCHAR,      nullable = False),
        Column('deadline',      TIMESTAMP,    nullable = False),
        Column('timeout',       INT,          nullable = False),
        Column('maxgrade',      INT,          nullable = False),

        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(['course_id'], ['courses.id']),
        UniqueConstraint('course_id', 'name'))

holidays = Table('holidays', metadata,
        Column('kickoff',       TIMESTAMP,    nullable = False),
        Column('finish',        TIMESTAMP,    nullable = False))

users = Table('users', metadata,
        Column('id',            INT),
        Column('username',      VARCHAR,      nullable = False),
        Column('fullname',      VARCHAR,      nullable = False),

        PrimaryKeyConstraint('id'),
        UniqueConstraint('username'))

teachers = Table('teachers', metadata,
        Column('user_id',       INT,          nullable = False),
        Column('course_id',     INT,          nullable = False),

        ForeignKeyConstraint(['user_id'], ['users.id']),
        ForeignKeyConstraint(['course_id'], ['courses.id']),
        UniqueConstraint('user_id', 'course_id'))

assistants = Table('assistants', metadata,
        Column('user_id',       INT,          nullable = False),
        Column('assignment_id', INT,          nullable = False),

        ForeignKeyConstraint(['user_id'], ['users.id']),
        ForeignKeyConstraint(['assignment_id'], ['assignments.id']),
        UniqueConstraint('user_id', 'assignment_id'))

submissions = Table('submissions', metadata,
        Column('id',            INT),
        Column('assignment_id', INT,          nullable = False),
        Column('user_id',       INT,          nullable = False),
        Column('upload',        TIMESTAMP,    nullable = False),
        Column('grade',         FLOAT,         nullable = False),

        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(['assignment_id'], ['assignments.id']),
        ForeignKeyConstraint(['user_id'], ['users.id']))

comments = Table('comments', metadata,
        Column('id',            INT),
        Column('submission_id', INT,          nullable = False),
        Column('user_id',       INT,          nullable = False),
        Column('filename',      VARCHAR),
        Column('line',          INT),
        Column('comment',       VARCHAR,      nullable = False),
        Column('delta',         FLOAT,        default = 0.0),

        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(['submission_id'], ['submissions.id']),
        ForeignKeyConstraint(['user_id'], ['users.id']))


from StringIO import StringIO

buff = StringIO()
engine = create_engine(
        'mysql://root:alfabet@localhost/vmchecker',
        strategy = 'mock',
        executor = lambda s, p = '': buff.write(s + p))
metadata.create_all(engine)

print buff.getvalue()
