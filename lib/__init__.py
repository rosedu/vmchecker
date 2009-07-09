from . import sql

class VmcheckerError(Exception):
    pass


class NoSuchAssignmentError(VmcheckerError):
    pass

class NoSuchUserError(VmcheckerError):
    pass



def get_assignment(assignment_id):
    """Queries the database for the assignment identified by `assignment_id'"""
    select = sql.assignments.select(sql.assignments.c.id == assignment_id)
    result = select.execute().fetchone()
    if result is None:
        raise NoSuchAssignmentError('Invalid assignment id %d' % assignment_id)
    return result


def get_user(user_id):
    """Queries the database for the user identified by `user_id'"""
    select = sql.assignments.select(sql.users.c.id == user_id)
    result = select.execute().fetchone()
    if result is None:
        raise NoSuchUserError
    return result


__all__ = ['submit']

