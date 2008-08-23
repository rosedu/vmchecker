/*
 * hello_test.c: test hello.c program
 * 
 *  example for vmchecker project - Windows C applications (OS course)
 *
 * (C) Razvan Deaconescu, 2008
 */

#include <windows.h>

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <assert.h>

#include "test_win.h"

#define PROGRAM_NAME	"hello.exe"
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
	HANDLE fHandle;
	BOOL ret;
	char buf[BUFSIZ];
	DWORD bytesRead;

	buf[HELLO_LEN] = '\0';

	fHandle = CreateFile(
			OUT_FILENAME,
			GENERIC_READ,
			FILE_SHARE_READ,
			NULL,
			OPEN_EXISTING,
			FILE_ATTRIBUTE_NORMAL,
			NULL);
	assert(fHandle != INVALID_HANDLE_VALUE);

	ret = ReadFile(
			fHandle,
			buf,
			HELLO_LEN,
			&bytesRead,
			NULL
		      );
	assert(ret == TRUE);
	do_test("string_present", bytesRead == HELLO_LEN && (strcmp(buf, HELLO_STRING) == 0));

	ret = ReadFile(
			fHandle,
			buf,
			HELLO_LEN,
			&bytesRead,
			NULL
		      );
	assert(ret == TRUE);
	do_test("string_only", bytesRead == 0);

	CloseHandle(fHandle);
}

static void cleanup(void)
{
	DeleteFile(OUT_FILENAME);
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
