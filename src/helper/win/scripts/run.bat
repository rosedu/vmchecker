::
:: [vmchecker] test run batch script - runs tests
::

:: run setup scripts
@ pushd .
@ call "\Program Files\Microsoft Visual Studio 8\Common7\Tools\vsvars32.bat" > NUL
@ call "\Program Files\Microsoft Platform SDK for Windows Server 2003 R2\SetEnv.cmd" /SRV32 > NUL
@ popd
@ echo on

:: run tests
nmake /nologo /f Makefile.checker pre-run
nmake /nologo /f Makefile.checker run
nmake /nologo /f Makefile.checker post-run
