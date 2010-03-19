#!/bin/sh

DIR=/home/szekeres/vmchecker/
 
rm -rdf $DIR && mkdir -p $DIR
cd $DIR


vmchecker-init-course storer


# create fake zip files for the test and user submission.
touch file
zip test.zip    file
zip archive.zip file

# place the test in the proper place
cp test.zip tests/1-minishell-linux.zip

vmchecker-submit SO 1-minishell-linux u1 archive.zip 
vmchecker-submit SO 1-minishell-linux u1 archive.zip  # resubmit!
vmchecker-submit SO 1-minishell-linux u2 archive.zip 
vmchecker-submit SO 1-minishell-linux u3 archive.zip 

vmchecker-resubmit -c SO --all
vmchecker-update-db -c SO -all

vmchecker-update-db -c SO --simulate --all
