# Copyright (c) 2008 Lucian Adrian Grijincu (lucian.grijincu@gmail.com)
# See LICENSE file for license details.


# One Makefile to rule them all, 
# 	one Makefile to find them, 
# 	one Makefile to bring them all, 
#	and in the darkness bind them.

MAKEFLAGS += --no-print-directory

COMPONENTS:= VMExecutor Commander

all:
	@echo " run make tester-dist or make storer-dist"


vmchecker_root_var:
	@if [ "x$VMCHECKER_ROOT" = "x" ]; then 		\
		echo "VMCHECKER_ROOT variable is not set";	\
		exit 1;						\
	fi

storer-dist: vmchecker_root_var
	./bin/initialise_course.py storer


tester-dist: vmchecker_root_var
	@bin/assert_python_modules_installed.py
	@for i in $(COMPONENTS); do \
		cd $$i && echo " -- Enter -- $$i to make $@" && $(MAKE) $@ && cd ..; \
	done;
	./bin/initialise_course.py tester
	mkdir -p ./executor_jobs/

clean:
	@for i in $(COMPONENTS); do \
		cd $$i && echo " -- Enter -- $$i to make $@" && $(MAKE) $@ && cd ..; \
	done;

	rm -vf bin/semctl bin/vm_executor bin/commander;
	rm -f *~
	rm -f bin/*~
