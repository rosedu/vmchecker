/*
 * log header
 */

#ifndef LOG_H_
#define LOG_H_	1

#include <stdio.h>

#define log(format, ...) \
	printf(format, ##__VA_ARGS__)

#define error(format, ...) \
	fprintf(stderr, "Error: " format, ##__VA_ARGS__)

#endif /* LOG_H_ */
