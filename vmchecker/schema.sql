-- vim: set filetype=sql: --

CREATE TABLE courses (
	cid INT NOT NULL AUTO_INCREMENT,
	name VARCHAR NOT NULL,

	PRIMARY KEY (cid),
	UNIQUE (name)
);

CREATE TABLE assignments (
	aid INT NOT NULL AUTO_INCREMENT,
	cid INT NOT NULL,                   -- assignment's course
	name VARCHAR NOT NULL,
	url VARCHAR,                        -- location of the assignment's text
	repository VARCHAR NOT NULL,        -- local repository path
	timeout INT NOT NULL,               -- how many seconds is a
	-- submission allowed to run
	maxgrade INT NOT NULL,              -- eg. 10 or 100

	PRIMARY KEY (aid),
	FOREIGN KEY (cid) REFERENCES courses(cid),
	UNIQUE (name, cid)
);

-- no penalty occurs during holidays
-- XXX per course?
CREATE TABLE holidays (
	kickoff DATE NOT NULL,              -- when the holiday starts
	finish DATE NOT NULL                -- when the holiday ends
);

-- The email & twitter fields will be used to inform the
-- user when the submission was evaluated.
CREATE TABLE users (
	uid INT NOT NULL AUTO_INCREMENT,
	username VARCHAR NOT NULL,          -- from LDAP
	fullname VARCHAR,                   -- from LDAP

	PRIMARY KEY (uid),
	UNIQUE (username)
);

-- Teachers can assign assistants to the course
CREATE TABLE teachers (
	uid INT NOT NULL,
	cid INT NOT NULL,                   -- course he/she is teaching

	FOREIGN KEY (uid) REFERENCES users(uid),
	UNIQUE (uid, cid)
);

-- Assistants can create grade assignments
CREATE TABLE assistants (
	uid INT NOT NULL,
	aid INT NOT NULL,                   -- assignment he/she can grade

	FOREIGN KEY (uid) REFERENCES users(uid),
	UNIQUE (uid, aid)
);

-- Each homework upload is called a submission.
CREATE TABLE submissions (
	sid INT NOT NULL AUTO_INCREMENT,
	aid INT NOT NULL,                   -- assignment id
	uid INT NOT NULL,                   -- user id
	upload DATE,                        -- when was it uploaded
	grade REAL,                         -- grade to be displayed, normally 

	PRIMARY KEY (sid),
	FOREIGN KEY (aid) REFERENCES assistants(aid),
	FOREIGN KEY (uid) REFERENCES users(uid)
);

CREATE TABLE comments (
	cid INT NOT NULL AUTO_INCREMENT,
	sid INT NOT NULL,                   -- submission id
	uid INT NOT NULL,                   -- who made the comment
	filename VARCHAR,                   -- if NULL, @submission
	line INT,                           -- if NULL, @file
	comment VARCHAR,                    -- comment
	delta REAL,                         -- adjusts grade

	PRIMARY KEY (cid),
	FOREIGN KEY (cid) REFERENCES courses(aid),
	FOREIGN KEY (aid) REFERENCES assistants(aid),
	FOREIGN KEY (uid) REFERENCES users(uid)
);
