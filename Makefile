# Copyright (c) 2008 Lucian Adrian Grijincu (lucian.grijincu@gmail.com)
# See LICENSE file for license details.


# One Makefile to rule them all, 
# 	one Makefile to find them, 
# 	one Makefile to bring them all, 
#	and in the darkness bind them.

MAKEFLAGS += --no-print-directory

COMPONENTS:= VMExecutor Commander semctl

all:
	echo " run make tester-dist or make uploader-dist"


uploader-dist:
	./bin/initialise_course.py


tester-dist:
	@for i in $(COMPONENTS); do \
		cd $$i && echo " -- Enter -- $$i to make $@" && $(MAKE) $@ && cd ..; \
	done;

clean:
	@for i in $(COMPONENTS); do \
		cd $$i && echo " -- Enter -- $$i to make $@" && $(MAKE) $@ && cd ..; \
	done;

	rm -vf bin/semctl bin/vm_executor bin/commander;
