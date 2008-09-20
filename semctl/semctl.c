/*
 * Create, modify and delete SysV semaphores
 *
 * Copyright (c) 2008Lucian Adrian Grijincu (lucian.grijincu@gmail.com)
 * See LICENSE file for license details.
 */


#include <sys/ipc.h>
#include <sys/sem.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>
// ftok crashes if the filename does not point to a valid file
// we create one in a place where we're sure we can create a file
// and where we don't polute the local namespace
#define FTOKPREFIX "/tmp/vmchecker_"

enum ACTIONS {
    UP,
    DOWN,
    CREATE,
    ERASE,
    EXISTS,
    INVALID_ACTION
};

static void print_usage(const char * program_name)
{
    fprintf(stderr,
            "%s [up|down|create|erase|exists] UniqueString [count]\n"
            " create [count]  - create a new semaphore with value count\n"
            "                 - default count value: 0\n"
            " up/down [count] - increment/decrement the semaphore with count\n"
            "                 - default count value: 1\n"
            " erase           - erase the semaphore\n"
            " exists          - check if a semaphore exists\n",
            program_name);
}

static void errmsg(const char * fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    fprintf(stderr, "[SEMCTL] ");
    vfprintf(stderr, fmt, ap);
    va_end(ap);
}

static void print_errno(const char * userstr, int err, ...)
{
    va_list ap;
    char * strerr = strerror(err);
    va_start(ap, err);
    fprintf(stderr, "[SEMCTL] ");
    vfprintf(stderr, userstr, ap);
    errmsg("\t(errno=[%d] strerr=[%s])\n", err, strerr);
    va_end(ap);
}


/////////////////////
// FILE OPERATIONS //
/////////////////////
static char * complete_ftok_filename(const char * str)
{
    char * ret = NULL;
    ret = (char*) calloc(strlen(FTOKPREFIX) + strlen(str) + 1, 1);
    memcpy(ret, FTOKPREFIX, strlen(FTOKPREFIX));
    memcpy(ret + strlen(FTOKPREFIX), str, strlen(str));
    return ret;
}

static int create_file(const char * ftokstr)
{
    int fd = 0;
    fd = creat(ftokstr,
               S_IRUSR | S_IWUSR |
               S_IRGRP | S_IWGRP |
               S_IROTH | S_IWOTH);
    if (-1 == fd) {
        print_errno("create_file:creat failed.", errno);
        return -1;
    }
    // will not close fd here.
    // it will be closed by the OS when process dies.
    // I want to be sure the file is there when we create the semaphore.
    //   close(fd);
    return 0;
}

static int erase_file(const char * ftokstr)
{
    int ret = 0;
    ret = unlink(ftokstr);
    if (-1 == ret) {
        print_errno("erase_file:unlink failed.", errno);
        return -1;
    }
    return 0;
}

static key_t my_ftok(const char * ftokstr)
{
#define GLOBAL_PROGRAM_ID 66 // a random number in the range [1..255]
    key_t key = ftok(ftokstr, GLOBAL_PROGRAM_ID);
    return key;
}



///////////////////
// SEMAPHORE OPS //
///////////////////

static int create_sem(key_t semKey)
{
    // create a semaphore
    // fail if the semaphore already exists.
    int ret = semget(semKey, 1, IPC_CREAT | IPC_EXCL | 0660);
    if (-1 == ret)
        print_errno("create_sem:semget failed", errno);
    return ret;
}

static int open_sem(key_t semKey)
{
    // open an existing semaphore
    int ret = semget(semKey, 1, 0);
    if (-1 == ret)
        print_errno("open_sem:semget failed", errno);
    return ret;
}

static int erase_sem(int semId)
{
    int ret = semctl(semId, 0 /* ignored */, IPC_RMID);
    if (-1 == ret)
        print_errno("erase_sem:semctl failed", errno);
    return ret;
}

static int modify_sem(int semId, int diff)
{
    int ret;
    struct sembuf sop;
    sop.sem_num = 0; // the first semaphore in the semaphore array
    sop.sem_op = diff;
    sop.sem_flg = 0;
    ret = semop(semId, &sop, 1);
    if (-1 == ret)
        print_errno("modify_sem:semop failed", errno);
    return ret;
}


///////////////////
// PROGRAM LOGIC //
///////////////////

static int run_action(enum ACTIONS action, const char * ftokstr, int count)
{
    key_t key = -1;
    int semId = -1;
    int err = 0;

    if (CREATE == action) {
        err = create_file(ftokstr);
        if (-1 == err)
            return -1;
    }


    key = my_ftok(ftokstr);
    if (-1 == key) {
        if (EXISTS == action) {
            printf("0\n");
            return 0;
        }
        print_errno("run_action:my_ftok failed. ftok args were\n"
                    "\t %s\n"
                    "\t %d\n", errno, ftokstr, GLOBAL_PROGRAM_ID);
        return -1;
    }

    switch(action) {
    case DOWN:
        count *= -1;
        /* fallthough */
    case UP:
        semId = open_sem(key);
        if (-1 == semId)
            return -1;
        return modify_sem(semId, count);

    case CREATE:
        // only creates the semaphore. does noting with it.
        semId = create_sem(key);
        if (-1 == semId)
            return -1;

        return modify_sem(semId, count);

    case ERASE:
        semId = open_sem(key);
        if (-1 == semId)
            return -1;

        // don't stop after erase_sem. kill any stale file too.
        err = erase_sem(semId);
        err |= erase_file(ftokstr);
        if (-1 == err)
            return -1;
        return 0;

    case EXISTS:

        semId = open_sem(key);
        if (-1 == semId)
            printf("0\n");
        else
            printf("1\n");
        return (-1 == semId);

    default:
        errmsg("run_action: invalid action=[%d]\n", action);
        return -1;
    }

    return -2;
}

static int
parse_args(int argc, char * argv[], char ** pftokstr,
           enum ACTIONS * pact, int * pcount) {
    *pftokstr = NULL;
    *pact = INVALID_ACTION;
    if (argc < 3) {
        errmsg("Invalid number of arguments.\n");
        return EXIT_FAILURE;
    }

#define PARSE_ACTION(action_name)                   \
    do {                                            \
        if (0 == strcasecmp(argv[1], #action_name)) \
            *pact = action_name;                    \
    } while (0)

    PARSE_ACTION(UP);
    PARSE_ACTION(DOWN);
    PARSE_ACTION(CREATE);
    PARSE_ACTION(ERASE);
    PARSE_ACTION(EXISTS);
#undef PARSE_ACTION

    if (INVALID_ACTION == *pact) {
        errmsg("Invalid first argument [%s].\n", argv[1]);
        return EXIT_FAILURE;
    }

    *pftokstr = complete_ftok_filename(argv[2]);

    if (argc >= 4) {
        char * endptr, * str;
        str = argv[3];
        errno = 0;    /* To distinguish success/failure after call */
        *pcount = strtol(str, &endptr, 10);

        /* Check for various possible errors */

        if ((errno == ERANGE && (*pcount == LONG_MAX || *pcount == LONG_MIN))
            || (errno != 0 && *pcount == 0)) {
            print_errno("could not parse `count` field", errno);
            return EXIT_FAILURE;
        }

        if (endptr == str) {
            errmsg("No digits were found in the `count` field.\n");
            return EXIT_FAILURE;
        }

        /* If we got here, strtol() successfully parsed a number */

        if (*endptr != '\0') {
            errmsg("`Count` field contained more than a number.\n");
            return EXIT_FAILURE;
        }
        return EXIT_SUCCESS;
    } else {
        *pcount = (*pact == CREATE) ? 0 : 1;
    }

    return EXIT_SUCCESS ;
}

int main(int argc, char * argv[])
{
    int count = 0;
    int err = 0;
    char * ftokstr = NULL;
    enum ACTIONS action;
    err = parse_args(argc, argv, &ftokstr, &action, &count);
    if (err) {
        errmsg("Invalid arguments (error code:%d)\n", err);
        print_usage(argv[0]);
        free(ftokstr);
        return err;
    }

    err = run_action(action, ftokstr, count);
    if (err) {
        errmsg("Cannot perform that action (error code:%d)\n", err);
        free(ftokstr);
        return EXIT_FAILURE;
    }
    free(ftokstr);
    return EXIT_SUCCESS;
}
