#ifndef TEST_LIN_H_
#define TEST_LIN_H_	1

/*
 * print a "failed" or "passed" message depending on the test's outcome
 *
 * message is printed as
 *   name.....................................passed (or failed)
 *
 * @name: test name (should be an easily identifiable value)
 * @value: result value; boolean; 0 means failed, 1 means passed
 */

static void do_test(const char *name, int value)
{
	unsigned int i;

        printf("test: %s", name);
	fflush(stdout);

	for (i = 0; i < 60-strlen(name); i++)
		putchar('.');
	if (value == 0)
		printf("failed (%s)\n", strerror(errno));
	else
		printf("passed\n");

	fflush(stdout);
}

#endif
