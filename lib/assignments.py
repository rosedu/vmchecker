from sqlalchemy.exceptions import IntegrityError, OperationalError

from . import VmcheckerError
from . import sql


def get(assignment_id):
    """Queries the database for the assignment identified by `assignment_id'"""
    select = sql.assignments.select(sql.assignments.c.id == assignment_id)
    result = select.execute().fetchone()
    return result


def create(course_id, name, url, repository, deadline, timeout, maxgrade):
    """Creates a new assignment an returns the new id"""
    insert = sql.assignments.insert()
    try:
        result = insert.execute(
                course_id = course_id,
                name = name,
                url = url,
                repository = repository,
                deadline = deadline,
                timeout = timeout,
                maxgrade = maxgrade)
        return result.last_inserted_ids()[0]
    except (IntegrityError, OperationalError), e:
        raise VmcheckerError('Cannot insert: %s' % str(e))
