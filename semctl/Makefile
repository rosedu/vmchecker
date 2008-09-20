# Copyright (c) 2008 Lucian Adrian Grijincu (lucian.grijincu@gmail.com)
# See LICENSE file for license details.

CFLAGS=-g -Wall

semctl: semctl.o

uploader-dist:# do nothing

tester-dist: semctl
	cp ./semctl ../bin/

clean:
	rm -f *~ semctl semctl.o
