#
# iniparser tests Makefile
#

CPPFLAGS  = -g -Wall -Iiniparser/src
LDFLAGS  = -Liniparser 
LDLIBS= -ldl -lstdc++ -liniparser 
AR	    = ar
ARFLAGS = rcv
RM      = rm -f


all:compile_parser commander

uploader-dist: # do nothing

tester-dist: all
		cp commander ../bin/

compile_parser: 
	cd iniparser;$(MAKE)

commander: commander.o
commander.o: commander.cpp

clean:
	$(RM) commander *.o *~
	cd iniparser; $(MAKE) clean


