#include <string.h>

#include <unistd.h>

#define HELLO_STRING	("Hello, world!\n")
#define HELLO_LEN	(strlen(HELLO_STRING))

int main(void)
{
	write(STDOUT_FILENO, HELLO_STRING, HELLO_LEN);

	return 0;
}
