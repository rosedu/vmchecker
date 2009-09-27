from . import sql


class VmcheckerError(Exception):
    pass


def get_user(user_id):
    """Queries the database for the user identified by `user_id'"""
    select = sql.assignments.select(sql.users.c.id == user_id)
    result = select.execute().fetchone()
    if result is None:
        raise NoSuchUserError
    return result
