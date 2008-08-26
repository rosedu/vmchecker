#
# [vmchecker] test deploy
#

deploy: assemble
	cd deploy/ && ./deploy.sh

assemble: _assign _tests _scripts

_assign:
	make -C assign/ pack
	cp assign/file.zip deploy/

_tests:
	make -C tests/ -f Makefile.checker pack
	cp tests/tests.zip deploy/

_scripts:
	cp scripts/* deploy/

clean:
	-rm -f *~
	-rm -f scripts/*~
	-rm -f deploy/*~
	-rm -f deploy/build.bat deploy/run.bat
	-rm -f deploy/build.sh deploy/run.sh
	-rm -f deploy/*.zip
	-rm -f deploy/*.txt
	-make -C assign/ clean
	-make -C tests/ -f Makefile.checker clean
