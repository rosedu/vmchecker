# See LICENSE file for license details.
MAKEFLAGS += --no-print-directory

COMPONENTS:= VMExecutor

all:
	@echo " run make tester-dist or make storer-dist"


storer-dist:
	./bin/initialise_course.py storer

tester-dist:
	@bin/assert_python_modules_installed.py paramiko pyinotify
	@for i in $(COMPONENTS); do \
		cd $$i && echo " -- Enter -- $$i to make $@" && $(MAKE) $@ && cd ..; \
	done;
	./bin/initialise_course.py tester
	mkdir -p ./executor_jobs/

clean:
	@for i in $(COMPONENTS); do \
		cd $$i && echo " -- Enter -- $$i to make $@" && $(MAKE) $@ && cd ..; \
	done;

	rm -vf bin/semctl bin/vm_executor
	rm -f *~ */*~
	rm -f bin/*~ bin/*.pyc
	@for d in queue tmpunzip; do				\
		if [ -d $$d ]; then				\
			rmdir  --ignore-fail-on-non-empty $$d;	\
		fi;						\
	done;
