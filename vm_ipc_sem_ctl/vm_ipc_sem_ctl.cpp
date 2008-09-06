#include <iostream>
#include <sys/ipc.h>
#include <sys/sem.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
using namespace std;
#define FTOKPREFIX "/tmp/vmchecker_"
#define FIRST_ERROR_CODE 100
enum ACTIONS {
    UP = FIRST_ERROR_CODE,
    DOWN,
    CREATE,
    ERASE,
    INVALID_ACTION
};

static void print_usage(const char * program_name)
{
    cerr << program_name << " [UP|DOWN|CREATE|ERASE] " << " CourseUniqueID\n";
}

static void print_errno(const char * usermgs, int err)
{
    char * strerr = strerror(err);
    cerr << usermgs << " (errno=[" << err << "] strerr=[" << strerr << "]\n";
}


/////////////////////
// FILE OPERATIONS //
/////////////////////
char * create_ftok_filename(const char * str)
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
    if (-1 == key) {
        cerr << "parse_args:ftok failed. ftok args were" << endl;
        cerr << "\t " << ftokstr << endl;
        cerr << "\t " << GLOBAL_PROGRAM_ID << endl;
        print_errno("", errno);
        return -1;
    }
    return key;
}



///////////////////
// SEMAPHORE OPS //
///////////////////
 
static int create_sem(key_t semKey)
{
    //cream o multime cu un singur semafor
    //apelul esueaza daca exista deja un semafor cu cheia din semKey
    int ret = semget(semKey, 1, IPC_CREAT | IPC_EXCL | 0660);
    if (-1 == ret)
        print_errno("create_sem:semget failed", errno);
    return ret;
}

static int open_sem(key_t semKey)
{
    //deschidem un semafor existent
    int ret = semget(semKey, 1, 0);
    if (-1 == ret)
        print_errno("open_sem:semget failed", errno);
    return ret;
}

static int erase_sem(int semId)
{
 	//cand comanda este IPC_RMID, al doilea parametru este ignorat
 	int ret = semctl(semId, 0, IPC_RMID);
    if (-1 == ret)
        print_errno("erase_sem:semctl failed", errno);
    return ret;    
}

static int modify_sem(int semId, int diff)
{
    int ret;
    struct sembuf sop;
    //ne referim la primul semafor din multime (cel cu numarul 0)
    sop.sem_num = 0;
    sop.sem_op = diff;
    sop.sem_flg = 0;
    ret = semop(semId, &sop, 1);
    if (-1 == ret)
        print_errno("modify_sem:semop failed", errno);
    return ret;
}

/*
  static int decrement_sem(int semId)
  {
  return modify_sem(semId, -1);
  }

  static int increment_sem(int semId)
  {
  return modify_sem(semId, +1);
  }
*/



///////////////////
// PROGRAM LOGIC //
///////////////////

static int run_action(enum ACTIONS action, const char * ftokstr)
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
    if (-1 == key)
        return -1;

    switch(action) {
    case UP:
    case DOWN:
        semId = open_sem(key);
        if (-1 == semId)
            return -1;
        return modify_sem(semId, (action==UP)?+1:-1);

    case CREATE:
        // only creates the semaphore. does noting with it.
        semId = create_sem(key);
        if (-1 == semId)
            return -1;
        return 0;

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

    default:
        cerr << "run_action: invalid action=[" << action << "]" << endl;
        return -1;
    }
    
    return -2;
}

static int 
parse_args(int argc, char * argv[], char * & ftokstr, enum ACTIONS & act) {
    ftokstr = NULL;
    act = INVALID_ACTION;
    if (argc < 3) {
        cerr << "Invalid number of arguments." << endl;
        return 1;
    }
#define PARSE_ACTION(action_name)                   \
    do {                                            \
        if (0 == strcasecmp(argv[1], #action_name)) \
            act = action_name;                      \
    }while(0);

    PARSE_ACTION(UP);
    PARSE_ACTION(DOWN);
    PARSE_ACTION(CREATE);
    PARSE_ACTION(ERASE);
    
    if (act == INVALID_ACTION) {
        cerr << "Invalid first argument [" << argv[1] << "]." << endl;
        return 2;
    }
    
    ftokstr = create_ftok_filename(argv[2]);
    return 0;
}

int main(int argc, char * argv[])
{
    int err = 0;
    char * ftokstr = NULL;
    enum ACTIONS action;
    err = parse_args(argc, argv, ftokstr, action);
    if (err) {
        cerr << "Invalid arguments (error code:" << err << ")" << endl;
        print_usage(argv[0]);
        free(ftokstr);
        return err;
    }
    
    err = run_action(action, ftokstr);
    if (err) {
        cerr << "Cannot perform that action (error code:" << err << ")" << endl;
        free(ftokstr);
        return err;
    }
    free(ftokstr);
    return 0;
}
