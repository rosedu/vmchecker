from sqlalchemy.exceptions import IntegrityError

from . import VmcheckerError
from . import sql


def get(course_id):
    """Queries the database for the course identified by `course_id'"""
    select = sql.courses.select(sql.courses.c.id == course_id)
    result = select.execute().fetchone()
    return result


def create(name):
    """Creates a new course an returns the new id"""
    insert = sql.courses.insert()
    try:
        result = insert.execute(name = name)
        return result.last_inserted_ids()[0]
    except IntegrityError, e:
        raise VmcheckerError('Cannot insert: %s' % str(e))
