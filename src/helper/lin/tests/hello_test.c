/*
 * hello_test.c: test hello.c program
 * 
 *  example for vmchecker project - Linux C applications (OS course)
 *
 * (C) Razvan Deaconescu, 2008
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>

#include <unistd.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>

#include "test_lin.h"

#define PROGRAM_NAME	"./hello"
#define OUT_FILENAME	"out.txt"

#define HELLO_STRING	("Hello, world!\n")
#define HELLO_LEN	(strlen(HELLO_STRING))

#ifndef BUFSIZ
#define BUFSIZ		1024
#endif

static void run_program(void)
{
	system(PROGRAM_NAME " > " OUT_FILENAME);
}

static void test_basic(void)
{
	int fd;
	ssize_t ret;
	char buf[BUFSIZ];

	buf[HELLO_LEN] = '\0';

	fd = open(OUT_FILENAME, O_RDONLY);
	assert(fd > 0);

	ret = read(fd, buf, HELLO_LEN);
	assert(ret >= 0);
	do_test("string_present", ret == HELLO_LEN && (strcmp(buf, HELLO_STRING) == 0));

	ret = read(fd, buf, HELLO_LEN);
	assert(ret >= 0);
	do_test("string_only", ret == 0);

	close(fd);
}

static void cleanup(void)
{
	unlink(OUT_FILENAME);
}

int main(void)
{
	/* run hello.exe program with redirected output */
	run_program();

	/* compare output file content with HELLO_STRING string */
	test_basic();

	/* do cleanup */
	cleanup();

	return 0;
}
