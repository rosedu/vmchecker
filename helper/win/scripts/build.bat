::
:: [vmchecker] build batch script - compiles assigments and tests
::

:: run setup scripts
@ pushd .
@ call "\Program Files\Microsoft Visual Studio 8\Common7\Tools\vsvars32.bat" > NUL
@ call "\Program Files\Microsoft Platform SDK for Windows Server 2003 R2\SetEnv.cmd" /SRV32 > NUL

:: cannot set DDK environment because of windows.h inclusion confusion
::@ set DDK_HOME=C:\WINDDK\3790.1830
::@ del /q /f %DDK_HOME%\build.dat
::@ call "%DDK_HOME%\bin\setenv.bat" %DDK_HOME% chk wnet > NUL

@ popd
@ echo on

:: build assignment
nmake /nologo pre-build
nmake /nologo build
nmake /nologo post-build

:: build tests
nmake /nologo /f Makefile.checker pre-build
nmake /nologo /f Makefile.checker build
nmake /nologo /f Makefile.checker post-build
