#
# iniparser tests Makefile
#

CPPFLAGS  = -g -Wall -Iiniparser/src
LDFLAGS  = -Liniparser 
LDLIBS= -ldl -lstdc++ -liniparser 
AR	    = ar
ARFLAGS = rcv
RM      = rm -f


all: commander 

commander:commander.o
commander.o: commander.cpp


clean veryclean:
	$(RM) commander *.o


