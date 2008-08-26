CFLAGS = /W3 /nologo
CC = cl

all: hello.exe

hello.exe: hello.obj
	link /nologo /out:$@ $**

hello.obj: hello.c

clean:
	del /q /f *.obj *~ *.bak hello.exe

pre-build:

# build hello.exe
build: hello.exe

post-build:

pack: hello.c Makefile
	zip file.zip hello.c Makefile
