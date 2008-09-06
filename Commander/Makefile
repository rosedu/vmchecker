#
# iniparser tests Makefile
#

CC      = gcc
CFLAGS  = -g -Iiniparser/src
LFLAGS  = -L.. -liniparser
AR	    = ar
ARFLAGS = rcv
RM      = rm -f


default: all

all: iniexample

iniexample: iniexample.c
	$(CC) $(CFLAGS) -o iniexample iniexample.c -I../src -Liniparser -liniparser


clean veryclean:
	$(RM) iniexample example.ini



