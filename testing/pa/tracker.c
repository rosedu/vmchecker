/**
 * @author claudiugh 
 * @file tracker.c 
 *
 * launches `make run` silently on current directory after 
 * redirecting the stdin and stdout to given files and sets 
 * limit on CPU execution time 
 * 
 * Arguments: 
 * argv[1]: timeout - currently in seconds 
 * argv[2]: input filename 
 * argv[3]: output filename 
 */

#include <stdlib.h> 
#include <string.h> 
#include <stdio.h>
#include <unistd.h> 
#include <errno.h>
#include <fcntl.h>
#include <sys/time.h> 
#include <sys/resource.h>
#include <sys/types.h> 
#include <sys/wait.h> 

#define MAKEFILE "Makefile"
#define MAKEFILE_TARGET "run"

void setup_job(int timeout, char *in, char *out) {
    struct rlimit limit;
    
    /* set the processor time limit */
    limit.rlim_cur = timeout; 
    limit.rlim_max = 2 * timeout; 
    setrlimit(RLIMIT_CPU, &limit);
    
    /* redirect input and output */
    int fd_in = open(in, O_RDONLY); 
    if (fd_in < 0) {
	fprintf(stderr, "Error opening job input file `%s`: %s\n", in, strerror(errno)); 
	exit(EXIT_FAILURE); 
    }

    if (dup2(fd_in, STDIN_FILENO) < 0) {
	fprintf(stderr, "Error duplicating input fd: %s\n", strerror(errno)); 
	exit(EXIT_FAILURE); 
    }
    
    int fd_out = open(out, O_WRONLY | O_CREAT | O_TRUNC, 0666); 
    if (fd_out < 0) {
	fprintf(stderr, "Error opening job output file `%s`: %s\n", out, strerror(errno)); 
	exit(EXIT_FAILURE); 
    }

    if (dup2(fd_out, STDOUT_FILENO) < 0) {
	fprintf(stderr, "Error duplicating output fd: %s\n", strerror(errno)); 
	exit(EXIT_FAILURE); 
    }

}

int main(int argc, char *argv[], char *const envp[]) {
    pid_t child_pid, w; 
    int status; 
    char *childargv[] = {"make", "-s", "--no-print-directory", "-f", MAKEFILE, MAKEFILE_TARGET, NULL}; 
    
    if (argc != 4) {
	fprintf(stderr, "Usage: ./tracker <timeout_seconds> <input_file> <output_file> \n"); 
	exit(EXIT_FAILURE);
    }

    int timeout = atoi(argv[1]); 

    child_pid = fork(); 
    if (-1 == child_pid) {
	fprintf(stderr, "Error in fork(): %s\n", strerror(errno)); 
	exit(EXIT_FAILURE); 
    } else if (0 == child_pid) {
	setup_job(timeout, argv[2], argv[3]); 
	execve("/usr/bin/make", childargv, envp);
	/* should not be here */
	fprintf(stderr, "Error in execve(): %s\n", strerror(errno)); 
	exit(EXIT_FAILURE); 
    } else { 
	struct rusage accounting; 
	w = wait4(child_pid, &status, 0, &accounting); 
	if (WEXITSTATUS(status)) {
	    /* we got an error */
	    return WEXITSTATUS(status); 
	} else {
	    /* print some stats */
	    fprintf(stdout, "time: %d.%d seconds\n", 
		    (int)accounting.ru_utime.tv_sec + (int)accounting.ru_stime.tv_sec,
		    (int)accounting.ru_utime.tv_usec + (int)accounting.ru_stime.tv_usec); 
	}
    }
    
    return 0; 
}


