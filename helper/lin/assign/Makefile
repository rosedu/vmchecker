CFLAGS = -Wall -g

all: hello

hello: hello.o

hello.o: hello.c

clean:
	rm -f *.o *~ *.bak hello *.zip

pre-build:

# build hello
build: hello

post-build:

pack: hello.c Makefile
	zip file.zip hello.c Makefile
