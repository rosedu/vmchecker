# Author: Lucian Adrian Grijincu (lucian.grijincu@gmail.com)
# Copyright (c) 2008 rosedu.org
# See LICENSE file for copyright and license details.


# One Makefile to rule them all, 
# 	one Makefile to find them, 
# 	one Makefile to bring them all, 
#	and in the darkness bind them.

MAKEFLAGS += --no-print-directory

COMPONENTS:= VMExecutor Commander semctl
dist clean:
	@for i in $(COMPONENTS); do \
		cd $$i && echo " -- Enter -- $$i to make $@" && $(MAKE) $@ && cd ..; \
	done;
