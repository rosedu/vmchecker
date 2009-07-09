-- vim: set filetype=mysql: --

DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
    id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR NOT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY (name)
);

DROP TABLE IF EXISTS assignments;
CREATE TABLE assignments (
    id INTEGER NOT NULL AUTO_INCREMENT,
    course_id INTEGER NOT NULL,             -- assignment's course
    name VARCHAR NOT NULL,
    url VARCHAR,                            -- location of the assignment's text
    repository VARCHAR NOT NULL,            -- local repository path
    deadline TIMESTAMP NOT NULL,            -- when is the assignment due
    timeout INTEGER NOT NULL,               -- how many seconds is a submission allowed to run
    maxgrade INTEGER NOT NULL,              -- eg. 10 or 100

    PRIMARY KEY (id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    UNIQUE KEY (name, course_id)
);

-- no penalty occurs during holidays
-- XXX per course?
DROP TABLE IF EXISTS holidays;
CREATE TABLE holidays (
    kickoff TIMESTAMP NOT NULL,             -- when the holiday starts
    finish TIMESTAMP NOT NULL               -- when the holiday ends
);

-- The email & twitter fields will be used to inform the
-- user when the submission was evaluated.
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER NOT NULL AUTO_INCREMENT,
    username VARCHAR NOT NULL,              -- from LDAP, eg. lgrijincu
    fullname VARCHAR NOT NULL,              -- from LDAP, eg. Lucian Adrian Grijincu

    PRIMARY KEY (id),
    UNIQUE KEY (username)
);

-- Teachers can assign assistants to the course
DROP TABLE IF EXISTS teachers;
CREATE TABLE teachers (
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,             -- course he/she is teaching

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    UNIQUE (user_id, course_id)
);

-- Assistants can create grade assignments
DROP TABLE IF EXISTS assistants;
CREATE TABLE assistants (
    user_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,         -- assignment he/she can grade

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    UNIQUE (user_id, assignment_id)
);

-- Each homework upload is called a submission.
DROP TABLE IF EXISTS submissions;
CREATE TABLE submissions (
    id INTEGER NOT NULL AUTO_INCREMENT,
    assignment_id INTEGER NOT NULL,         -- assignment id
    user_id INTEGER NOT NULL,               -- user id
    upload TIMESTAMP,                       -- when was it uploaded
    grade REAL,                             -- grade to be displayed, normally 

    PRIMARY KEY (id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS comments;
CREATE TABLE comments (
    id INTEGER NOT NULL AUTO_INCREMENT,
    submission_id INTEGER NOT NULL,         -- what submission was commented
    user_id INTEGER NOT NULL,               -- who made the comment
    filename VARCHAR,                       -- if NULL, @submission
    line INTEGER,                           -- if NULL, @file
    comment VARCHAR NOT NULL,               -- comment
    delta REAL,                             -- adjusts grade

    PRIMARY KEY (id),
    FOREIGN KEY (submission_id) REFERENCES submissions(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

