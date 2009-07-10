"""Functions to store a submission and send it for evaluation"""

import shutil
import os

from . import sql, VmcheckerError


SOURCES_FILE = 'sources.zip'


def store(archive, assignment_id, user_id, upload = None):
    """Stores archive into the corresponding location.

    Submission is stored at:
        <assignment.repository>/<submission_id>/<SOURCES_FILE>

    @param archive path to the archive
    @param assignment_id the assignment solved
    @param user_id the author of the submission
    @param upload if not None a `datetime' object containg the upload time
    @return a pair (submission_id, path)

    """

    try:
        transaction = sql.connection.begin()

        # reads the assignment from the repository
        select = sql.assignments.select().where(
                sql.assignments.c.id == assignment_id)
        assignment = sql.connection.execute(select).fetchone()

        # creates a new submission
        insert = sql.submissions.insert().values(
                assignment_id = assignment_id,
                user_id = user_id,
                upload = upload,
                grade = assignment.maxgrade)
        result = sql.connection.execute(insert)

        submission_id = result.last_inserted_ids()[0]
        location = os.path.join(assignment.repository, str(submission_id))

        if os.path.lexists(location):
            # cleans old files left from a failed
            # transaction
            shutil.rmtree(location)

        # copy fles
        os.makedirs(location)
        shutil.copy(archive, os.path.join(location, SOURCES_FILE))

        transaction.commit()
        return submission_id, location
    except VmcheckerError:
        transaction.rollback()
        raise


