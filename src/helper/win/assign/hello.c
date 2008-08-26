#include <windows.h>

#define HELLO_STRING	("Hello, world!\n")
#define HELLO_LEN	(strlen(HELLO_STRING))

int main(void)
{
	DWORD bytesWritten;

	WriteFile(
			GetStdHandle(STD_OUTPUT_HANDLE),
			HELLO_STRING,
			HELLO_LEN,
			&bytesWritten,
			NULL);

	return 0;
}
