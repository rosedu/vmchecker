#
# VMchecker - compile C client
#

# development
CXXFLAGS = -Wall -g -Weffc++
# release
#CFLAGS = -Wall -O -Weffc++

VIX_INCLUDE_PATH = /usr/include/vmware-vix/
VIX_LIB_PATH = /usr/lib/vmware-vix/lib/server-1/32bit/
CPPFLAGS = -I$(VIX_INCLUDE_PATH)
LDFLAGS = -L$(VIX_LIB_PATH)
LDLIBS = -ldl -lvix -lstdc++

.PHONY: all clean dist test_lin test_win

all: vm_executor

uploader-dist: # do nothing

tester-dist: all
	cp ./vm_executor ../bin/

vm_executor: vm_executor.o 

vm_executor.o: vm_executor.cpp vm_executor.h 

clean:
	-rm -f vm_executor *.o *~

test_lin: checker
	cp lin_file.zip file.zip
	cp lin_tests.zip tests.zip
	./checker lin 0 "2008-07-26 16:17:20" "2008-07-30 18:21:43" 25

test_win: checker
	cp win_file.zip file.zip
	cp win_tests.zip tests.zip
	./checker win 0 "2008-07-26 16:17:20" "2008-07-30 18:21:43" 25
