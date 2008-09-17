
# One Makefile to rule them all, 
#  one Makefile to find them, 
#  one Makefile to bring them all, 
#  and in the darkness bind them.
# Lucian Adrian Grijincu (lucian.grijincu@gmail.com)

MAKEFLAGS += --no-print-directory

dist clean:
	@cd VMExecutor 	&& echo " -- Enter --  VMExecutor" && $(MAKE) $@
	@cd Commander 	&& echo " -- Enter --  Commander " && $(MAKE) $@
	@cd semctl		&& echo " -- Enter --  semctl    " && $(MAKE) $@

