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

compile_parser: 
	cd iniparser;$(MAKE)
	
commander: commander.o
commander.o: commander.cpp

veryclean:
	$(RM) commander *.o
	cd iniparser;$(MAKE) veryclean


