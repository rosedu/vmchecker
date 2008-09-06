#
# iniparser tests Makefile
#

CXXFAGS= -g -Wall

CPPFLAGS  = -Iiniparser/src
LDFLAGS  = -Liniparser 
LDLIBS= -ldl -lstdc++ -liniparser -lfl
AR	    = ar
ARFLAGS = rcv
RM      = rm -f


all: commander 

commander:commander.o
commander.o: commander.cpp


clean veryclean:
	$(RM) commander *.o


