#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "iniparser.h"

int  parse_ini_file(char * ini_name);

int main(int argc, char * argv[])
{
	int status ;

	if (argc==2) {
		status = parse_ini_file(argv[1]);
	}
	return status ;
}

int parse_ini_file(char * ini_name)
{
	dictionary* ini ;

	ini = iniparser_load(ini_name);
	if (ini==NULL) {
		fprintf(stderr, "cannot parse file: %s\n", ini_name);
		return -1 ;
	}
//	iniparser_dump(ini, stderr);

	printf("Fisier configurare tema\n");
	
	printf("Job=%s\n",(char*) iniparser_getstring(ini, "Global:Job",NULL));
	
	iniparser_freedict(ini);
	return 0 ;
}


