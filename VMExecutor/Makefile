#
# VMchecker - compile C client
#

# development
CXXFLAGS = -Wall -g
# release
#CFLAGS = -Wall -O

VIX_INCLUDE_PATH = /usr/include/vmware-vix/
VIX_LIB_PATH = /usr/lib/vmware-vix/lib/server-1/32bit/
CPPFLAGS = -I$(VIX_INCLUDE_PATH)
LDFLAGS = -L$(VIX_LIB_PATH)
LDLIBS = -ldl -lvix -lstdc++ -lfl

.PHONY: all clean

all: checker

checker: checker.o 

checker.o: checker.cpp checker.h 

clean:
	-rm -f checker *~ *.o job_output job_run job_results job_build \
		checker_conf_reader.c

test_lin: checker
	cp lin_file.zip file.zip
	cp lin_tests.zip tests.zip
	./checker lin 0 "2008-07-26 16:17:20" "2008-07-30 18:21:43" 25

test_win: checker
	cp win_file.zip file.zip
	cp win_tests.zip tests.zip
	./checker win 0 "2008-07-26 16:17:20" "2008-07-30 18:21:43" 25
