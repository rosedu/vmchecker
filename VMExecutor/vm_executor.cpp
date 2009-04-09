/*------------------------- 78 characters line -----------------------------*/
/*----------------------- NO BIGGER LINES ALLOWED :D -----------------------*/
/**
   @file	vm_executor.cpp
   @author	Adriana Szekeres <aaa_sz@yahoo.com>
   @date	September 2008
   @version	Version 1.0 Release 1
   @brief	Communicates with Virtual Machines - using VIX API

   Coding issues, Razvan Deaconescu <razvan@rosedu.org>

     This module starts the specified Virtual Machine, copies from the Tester
   System  the  two  archives  (file.zip  and tests.zip) and  the two scripts
   (build.sh and run.sh)  on  the Virtual  Machine, starts the scripts in the
   Virtual Machine and collects the results.
*/
/*--------------------------------------------------------------------------*/
#include <iostream>
#include <assert.h>
#include <fstream>
#include <sstream>
#include <string>
#include <cstdlib>
#include <stdio.h>
#include <time.h>
#include <vector>
#include <signal.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>


#include <vix.h>

using namespace std;

#include "debug.h"
#include "log.h"
#include "vm_executor.h"

/*--------------------------------------------------------------------------*/
/*--------------------- Global Variables -----------------------------------*/
/* running information */
static struct run_struct vmrun={""};

/* define global variables */
static VixError err = VIX_OK;
static VixHandle hostHandle = VIX_INVALID_HANDLE;
static VixHandle jobHandle = VIX_INVALID_HANDLE;
static VixHandle vmHandle = VIX_INVALID_HANDLE;
static VixHandle snapshotHandle = VIX_INVALID_HANDLE;

static int snapshotIndex;
static int pid_nc = -1;
static string temp;

string jobs_path;
string scripts_path;

Bool jobCompleted;
/*--------------------------------------------------------------------------*/

/*--------------------- Functions code -------------------------------------*/
/*--------------------------------------------------------------------------*/
/**
    This  function  fills vmrun  structure  with  virtual machine information
  received  from  Commander  module.  "vmrun"  is  a  structure  declared  in
  "vm_executor.h" header file. Its members are described in the configuration
  files.

  @param    argv : array of char* containing the arguments received from
                   Commander
*/
/*--------------------------------------------------------------------------*/
static int fill_vmrun( char **argv)
{
	//char *endp;

	vmrun.vmname = argv[1];

	// read the km_enable flag
	if (strcmp(argv[2], "0") != 0) {
		if (strcmp(argv[2], "1") != 0) {
			fprintf(stderr, "[VMEXECUTOR] Usage error.\n");
			return -1;
		}
		else {
			vmrun.km_enable = true;
		}
	}
	else {
		vmrun.km_enable = false;
	}

	vmrun.vmpath = argv[3];
	vmrun.local_ip = argv[4];
	vmrun.guest_user = argv[5];
	vmrun.guest_pass = argv[6];
	vmrun.guest_home = argv[7];
	vmrun.guest_shell = argv[8];
	vmrun.guest_home_in_bash = argv[9];
	vmrun.vmchecker_root = argv[10];
	vmrun.job_id = argv[11];
	{
	  char * timeout_str = argv[12];
	  std::istringstream strreader(timeout_str);
	  if (!(strreader >> vmrun.timeout)) {
	    fprintf(stderr, "[VMEXECUTOR] Argument [%s] is not a valid timeout value",
		    timeout_str);
	    return -1;
	  }
	}
	vmrun.build_command_args = vmrun.build_command_args + 		     \
	" --login " +							     \
	"-c \" chmod +x " + vmrun.guest_home_in_bash + "/" + BUILD_SCRIPT +  \
	";" + vmrun.guest_home_in_bash + "/"+ BUILD_SCRIPT + " " + 	     \
	vmrun.guest_home_in_bash + " " + vmrun.local_ip + " " + 	     \
	vmrun.job_id + " \"";

	vmrun.run_command_args = vmrun.run_command_args + " --login -c \" chmod +x "  \
	+ vmrun.guest_home_in_bash + "/" + RUN_SCRIPT + ";" + 		     \
	vmrun.guest_home_in_bash + "/" + RUN_SCRIPT + " " + 		     \
	vmrun.guest_home_in_bash + " \"";

	jobs_path = vmrun.vmchecker_root + "/executor_jobs/";
	scripts_path = vmrun.vmchecker_root + "/executor_scripts/";

	return 0;
}

/*--------------------------------------------------------------------------*/
/**
    This  function prints information about the current job.
*/
/*--------------------------------------------------------------------------*/
static void print_run(void)
{
	cout << "=== Running job ===" << endl;
	cout << "vmname: " << vmrun.vmname << endl;
	cout << "vmdesc: " << vmrun.vmdesc << endl;
	cout << "guest_user: " << vmrun.guest_user << endl;
	cout << "guest_pass: " << vmrun.guest_pass << endl;
	cout << "guest_home: " << vmrun.guest_home << endl;
	cout << "guest_shell: " << vmrun.guest_shell << endl;
	cout << "local_ip: " << vmrun.local_ip << endl;
	cout << "build_command_args: " << vmrun.build_command_args << endl;
	cout << "run_command_args: " << vmrun.run_command_args << endl;
	cout << "km_enable: " << (vmrun.km_enable == true ? "true" : "false")\
	     << endl;
	cout << "===================" << endl;
}

/*--------------------------------------------------------------------------*/
/**
    This function  reads  the second line from BUILD_OUTPUT_FILE (the file
  that contains tests  and  homework  building results) which contains the
  IP address of the Virtual Machine. Currently, the IP address is obtained
  by  running  a  command  (written in build.sh) in  the  Virtual  Machine
  (ex. ifconfig/ipconfig).
*/
/*--------------------------------------------------------------------------*/
static int get_vm_ip()
{
	string line;


	ifstream infile((temp+jobs_path+BUILD_OUTPUT_FILE).c_str());

	if (! infile.is_open())
	{
		error("unable to open file %s\n",BUILD_OUTPUT_FILE);
		return -1;
	}

	getline(infile, vmrun.guest_ip);
	getline(infile, vmrun.guest_ip);	//ip on second line

	infile.close();

	return 0;
}

/*--------------------------------------------------------------------------*/
/**
    This function  checks if homework's building was succesful.

  @return  -1 if something baaad happened
            0 if building was not succesful
            number of warnings found + 1  if building was succesful
*/
/*--------------------------------------------------------------------------*/
static int check_build(void)
{
	string line;
	string oldline;
	string temp;

        ifstream infile((temp+jobs_path+BUILD_OUTPUT_FILE).c_str(),ios::in);

	int warning_count = 0;

	if (!infile.is_open())
	{
		error("[EXECUTOR] Unable to open file %s\n",
				BUILD_OUTPUT_FILE);
		error("[EXECUTOR] Unable to open file %s\n",
				(temp+jobs_path+BUILD_OUTPUT_FILE).c_str());
		return -1;
	}

	while (!infile.eof())
	{
		getline(infile,line);
		if(line.find("checker: building") != string::npos)
			break;
	}

	// we arrived at EOF if we could not find "checker: building" in the file
	if (infile.eof())
	{
		infile.close();
		error("[EXECUTOR] did not find a `checker: building` string in %s\n",
				BUILD_OUTPUT_FILE);
		return -2;
	}

	while (!infile.eof())
	{
		oldline = line;
		getline(infile, line);
		if (line.find(": warning") != string::npos ||
				line.find("warning:") != string::npos)
			warning_count++;
	}

	infile.close();

	if(oldline.find("failed") != string::npos)
		return 0;

	return warning_count + 1;
}

/*--------------------------------------------------------------------------*/
/**
    This function  uses VIX API to  start the Virtual Machine. It doesn't
  power it on, it reverts it from a snapshot (it is quicker and you don't
  have to delete the files you put on it).
*/
/*--------------------------------------------------------------------------*/
static int start_vm(void)
{
	int tries;

	log("[EXECUTOR] Connecting to server...\n");
	jobHandle = VixHost_Connect(
			1,
			VIX_SERVICEPROVIDER_VMWARE_SERVER,
			"",			// *hostName,
			0,			// hostPort,
			"",			// *userName,
			"",			// *password,
			0,			// options,
			VIX_INVALID_HANDLE,	// propertyListHandle,
			NULL,			// *callbackProc,
			NULL);			// *clientData);

	err = VixJob_Wait(jobHandle,
			VIX_PROPERTY_JOB_RESULT_HANDLE,
			&hostHandle,
			VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
   		error("[EXECUTOR] VixHost_Connect: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
   		return -1;
	}

	Vix_ReleaseHandle(jobHandle);

	log("[EXECUTOR] Opening VM...\n");
	jobHandle = VixVM_Open(
			hostHandle,
			vmrun.vmpath.c_str(),
			NULL,			// callbackProc
			NULL);			// clientData

	err = VixJob_Wait(
			jobHandle,
			VIX_PROPERTY_JOB_RESULT_HANDLE,
			&vmHandle,
			VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("[EXECUTOR] VixVM_Open: %s: %s %llu\n",
				Vix_GetErrorText(err,NULL), vmrun.vmpath.c_str(), err);
		return -1;
	}

	Vix_ReleaseHandle(jobHandle);

	log("[EXECUTOR] Getting SnapShot...\n");

	// revert to snapshot #0
	snapshotIndex = 0;
	err = VixVM_GetRootSnapshot(
			vmHandle,
			snapshotIndex,
			&snapshotHandle);
	if (VIX_OK != err)
	{
		error("[EXECUTOR] VixVM_GetRootSnapshot: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
   		return -1;
	}

	log("[EXECUTOR] Reverting to SnapShot...\n");
	jobHandle = VixVM_RevertToSnapshot(
			vmHandle,
			snapshotHandle,
			0,			// options
			VIX_INVALID_HANDLE,	// propertyListHandle
			NULL,			// callbackProc
			NULL);			// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("[EXECUTOR] VixVM_RevertToSnapshot: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		return -1;
	}

	log("[EXECUTOR] Waiting for Tools...\n");

	// wait until guest completes bootup process
	tries=5;
	while (tries>0)
	{
		jobHandle = VixVM_WaitForToolsInGuest(
				vmHandle,
				300,		// timeoutInSeconds
				NULL,		// callback
				NULL);		// clientData
		err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
		if (VIX_OK != err)
		{
			if (VIX_E_UNRECOGNIZED_PROPERTY == err)
			{
			log("[EXECUTOR] Retrying Waiting "
				"for Tools...\n");
				tries--;
				continue;
			}

			error("[EXECUTOR] "
			      "VixVM_WaitForToolsInGuest: %s: %llu\n",
					Vix_GetErrorText(err,NULL), err);
			return -1;
		}

		break;
	}

	log("[EXECUTOR] Logging in...\n");

	// authenticate for guest operations.
	jobHandle = VixVM_LoginInGuest(
			vmHandle,
			vmrun.guest_user.c_str(),
			vmrun.guest_pass.c_str(),
			0,			// options
			NULL,			// callbackProc
			NULL);			// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("[EXECUTOR] VixVM_LoginInGuest: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		// TODO: XXX - we print the pass to the console here.
		error("[EXECUTOR] VixVM_LoginInGuest: params were user=%s, pass=%s.\n",
				vmrun.guest_user.c_str() , vmrun.guest_pass.c_str());
		return -1;
	}

	return 0;
}

/*--------------------------------------------------------------------------*/
/**
    This function copies the necessary files on the Virtual Machine
*/
/*--------------------------------------------------------------------------*/
static int copy_files(void)
{
	string temp;
	// copy checker archive
	log("[EXECUTOR] Copying %s...\n", CHECKER_FILE);

	jobHandle = VixVM_CopyFileFromHostToGuest(
			vmHandle,
			(temp+jobs_path + CHECKER_FILE).c_str(),
			(vmrun.guest_home + CHECKER_FILE).c_str(),
			0,				// options
			VIX_INVALID_HANDLE,		// propertyListHandle
			NULL,				// callbackProc
			NULL);				// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("[EXECUTOR] VixVM_CopyFileFromHostToGuest: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		error("[EXECUTOR] VixVM_CopyFileFromHostToGuest: CHECKER_FILE"
		      "hostpath=%s guestpath=%s\n",
		      (temp+jobs_path + CHECKER_FILE).c_str(),
		      (vmrun.guest_home + CHECKER_FILE).c_str());
		return -1;
	}

	// copy CHECKER_TEST.zip
	log("[EXECUTOR] Copying %s...\n", CHECKER_TEST);
	jobHandle = VixVM_CopyFileFromHostToGuest(
			vmHandle,
			(temp+jobs_path+ CHECKER_TEST).c_str(),
			(vmrun.guest_home + CHECKER_TEST).c_str(),
			0,				// options
			VIX_INVALID_HANDLE,		// propertyListHandle
			NULL,				// callbackProc
			NULL);				// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("[EXECUTOR] VixVM_CopyFileFromHostToGuest: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		error("[EXECUTOR] VixVM_CopyFileFromHostToGuest CHECKER_TEST : "
		      "hostpath=%s guestpath=%s\n",
		      (temp+jobs_path + CHECKER_TEST).c_str(),
		      (vmrun.guest_home + CHECKER_TEST).c_str());
		{
		  int ret;
		  struct stat st;
		  const char * hostpath = (temp+jobs_path+ CHECKER_TEST).c_str();
		  ret = stat(hostpath, &st);
		  if (ret == -1)
		    perror("stat failed for CHECKER_TEST:");
		}
		return -1;
	}

        // copy build script
	log("[EXECUTOR] Copying %s...\n", BUILD_SCRIPT);
	jobHandle = VixVM_CopyFileFromHostToGuest(
			vmHandle,
			(temp + scripts_path + vmrun.vmname + "_"	     \
			+ BUILD_SCRIPT).c_str(),
			(vmrun.guest_home + BUILD_SCRIPT).c_str(),
			0,				// options
			VIX_INVALID_HANDLE,		// propertyListHandle
			NULL,				// callbackProc
			NULL);				// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("[EXECUTOR] VixVM_CopyFileFromHostToGuest: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		error("[EXECUTOR] VixVM_CopyFileFromHostToGuest BUILD_SCRIPT : "
		      "hostpath=%s guestpath=%s\n",
		      (temp + scripts_path + vmrun.vmname + "_" + BUILD_SCRIPT).c_str(),
		      (vmrun.guest_home + BUILD_SCRIPT).c_str());
		{
		  int ret;
		  struct stat st;
		  const char * hostpath = (temp + scripts_path + vmrun.vmname + "_" + BUILD_SCRIPT).c_str();
		  ret = stat(hostpath, &st);
		  if (ret == -1)
		    perror("stat failed for CHECKER_TEST:");
		}
		return -1;
	}

	// copy running script
	log("[EXECUTOR] Copying %s...\n", RUN_SCRIPT);
	jobHandle = VixVM_CopyFileFromHostToGuest(
			vmHandle,
			(temp+scripts_path +vmrun.vmname+"_"		     \
			+ RUN_SCRIPT).c_str(),
			(vmrun.guest_home + RUN_SCRIPT).c_str(),
			0,				// options
			VIX_INVALID_HANDLE,		// propertyListHandle
			NULL,				// callbackProc
			NULL);				// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("[EXECUTOR] VixVM_CopyFileFromHostToGuest: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		error("[EXECUTOR] VixVM_CopyFileFromHostToGuest: RUN_SCRIPT host=%s, guest=%s\n",
		      (temp+scripts_path + vmrun.vmname + "_" + RUN_SCRIPT).c_str(),
		      (vmrun.guest_home + RUN_SCRIPT).c_str());
		return -1;
	}

	return 0;
}

/*--------------------------------------------------------------------------*/
/**
    Handler function for SIGALRM
*/
/*--------------------------------------------------------------------------*/
static void alarm_handler(int sig)
{
	/* do nothing; succesfully */
}

/*--------------------------------------------------------------------------*/
/**
    Sets SIGALRM signal.
*/
/*--------------------------------------------------------------------------*/
static void set_signal()
{
	sigset_t imask,omask;
	struct sigaction act, oact;

	sigemptyset(&imask);
	sigemptyset(&omask);
	sigaddset(&imask, SIGALRM);

	memset(&act, 0, sizeof(act));
	sigemptyset(&act.sa_mask);
	act.sa_handler = alarm_handler;
	act.sa_flags = 0;
	sigaction(SIGALRM, &act, &oact);
}

/*--------------------------------------------------------------------------*/
/**
    Callback  function  for  RunProgramInGuest. This is called, if set
  accordingly,  when  a  program  running  on the Virtual Machine, has
  finished   its  execution. It  is  used  in implementing the timeout
  for a running homework.
*/
/*--------------------------------------------------------------------------*/
static void run_cb(VixHandle jobHandle, VixEventType eventType,
		VixHandle eventInfo, void* clientData)
{
	alarm(1);
}

/*--------------------------------------------------------------------------*/
/**
   This  function  runs the  two scripts in the Virtual Machine, checks if
  building was succesful and collects the results from the Virtual Machine..
*/
/*--------------------------------------------------------------------------*/
static int run_scripts(void)
{
	int build_c = 0;
	int timeout;

	ofstream outfile((temp+jobs_path+RESULT_OUTPUT_FILE).c_str());

	if (!outfile.is_open())
	{
		error("[EXECUTOR] Unable to open "
		      "file %s\n", RESULT_OUTPUT_FILE);
		return -1;
	}

	// run the target program.
	log("[EXECUTOR] Starting %s... prog=[%s] args[%s]\n", BUILD_SCRIPT,
	    vmrun.guest_shell.c_str(), vmrun.build_command_args.c_str());
	jobHandle = VixVM_RunProgramInGuest(
			vmHandle,
			vmrun.guest_shell.c_str(),
			vmrun.build_command_args.c_str(),
			0,			// options,
			VIX_INVALID_HANDLE,	// propertyListHandle,
			NULL,			// callbackProc,
			NULL);			// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("VixVM_RunProgramInGuest: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		error("VixVM_RunProgramInGuest: BUILD_SCRIPT prog=%s: args=%s ",
		      vmrun.guest_shell.c_str(),
		      vmrun.build_command_args.c_str());

		return -1;
	}


	// get BUILD_OUTPUT_FILE
	log("[EXECUTOR] Fetching %s...\n", BUILD_OUTPUT_FILE);

	jobHandle = VixVM_CopyFileFromGuestToHost(
			vmHandle,
			(vmrun.guest_home + BUILD_OUTPUT_FILE).c_str(),
			(temp+jobs_path + BUILD_OUTPUT_FILE).c_str(),
			0,			// options
			VIX_INVALID_HANDLE,	// propertyListHandle
			NULL,			// callbackProc
			NULL);			// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
                error("[EXECUTOR] VixVM_CopyFileFromGuestToHost: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
                error("[EXECUTOR] VixVM_CopyFileFromGuestToHost: BUILD_OUTPUT_FILE guest=%s: host=%s\n",
		      (vmrun.guest_home + BUILD_OUTPUT_FILE).c_str(),
		      (temp+jobs_path + BUILD_OUTPUT_FILE).c_str());
		return -1;
	}

	//check if build succesful
	build_c = check_build();

	if (build_c <= 0)
	{
        	outfile << "0" << endl;
        	outfile << "-10: tema nu se compileaza" << endl;
        	outfile.close();
        	return build_c;
    	}
    	else
    	{
        	outfile << "ok" << endl;
    	}

	//get_vm_ip
	if (get_vm_ip() == -1)
	{
		error("[EXECUTOR] System error: get_vm_ip failed\n");
		//return -2;
	}

	log("[EXECUTOR] VM's IP = %s\n", vmrun.guest_ip.c_str());

	//build succesful, go on with runnig RUN_SCRIPT

	/* setup alarm signal to be sent after vmrun.timeout seconds */
	set_signal();
	alarm(vmrun.timeout);

	// run the target program.
	log("[EXECUTOR] Starting %s... exe=[%s] args[%s]\n", RUN_SCRIPT,
	    vmrun.guest_shell.c_str(), vmrun.run_command_args.c_str());
	jobHandle = VixVM_RunProgramInGuest(
			vmHandle,
			vmrun.guest_shell.c_str(),
			vmrun.run_command_args.c_str(),
			0,			// options,
			VIX_INVALID_HANDLE,	// propertyListHandle,
			&run_cb,		// callbackProc,
			NULL);			// clientData

	// simple block - wait for it ...
	{
		time_t pre_time, post_time;

		pre_time = time(NULL);
		pause();
		post_time = time(NULL);
		timeout = post_time - pre_time;
	}

	log("[EXECUTOR] Timeout= %d\n",timeout);

	// get RUN_OUTPUT_FILE
	log("[EXECUTOR] Fetching %s...\n", RUN_OUTPUT_FILE);
	jobHandle = VixVM_CopyFileFromGuestToHost(
			vmHandle,
			(vmrun.guest_home + RUN_OUTPUT_FILE).c_str(),
			(temp+jobs_path + RUN_OUTPUT_FILE).c_str(),
			0,				// options
			VIX_INVALID_HANDLE,		// propertyListHandle
			NULL,				// callbackProc
			NULL);				// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
                error("[EXECUTOR] VixVM_CopyFileFromGuestToHost: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
                error("[EXECUTOR] VixVM_CopyFileFromGuestToHost: RUN_OUTPUT_FILE guest=%s host=%s\n",
		      (vmrun.guest_home + RUN_OUTPUT_FILE).c_str(),
		      (temp+jobs_path + RUN_OUTPUT_FILE).c_str());
		return -1;
	}

	//if kernel messages enabled, fetch KMESSAGE_OUTPUT_FILE
	if (vmrun.km_enable)
	{
		log("[EXECUTOR] Fetching %s...\n", KMESSAGE_OUTPUT_FILE);
		if (vmrun.vmname == "win")
		{
			jobHandle = VixVM_CopyFileFromGuestToHost(
				vmHandle,
				(vmrun.guest_home + 			     \
				KMESSAGE_OUTPUT_FILE).c_str(),
				(temp + jobs_path + 			     \
				KMESSAGE_OUTPUT_FILE).c_str(),
				0,			// options
				VIX_INVALID_HANDLE,	// propertyListHandle
				NULL,			// callbackProc
				NULL);			// clientData

			err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
			if (VIX_OK != err)
			{
				error("[EXECUTOR] VixVM_CopyFileFromGuestToHost: %s: %llu\n",
				      Vix_GetErrorText(err,NULL), err);
				error("[EXECUTOR] VixVM_CopyFileFromGuestToHost:KMESSAGE_OUTPUT_FILE guest=%s host=%s\n",
				      (vmrun.guest_home + KMESSAGE_OUTPUT_FILE).c_str(),
				      (temp + jobs_path + KMESSAGE_OUTPUT_FILE).c_str());

				return -1;
			}
		}


	}

	if(build_c > 1)
	{
		ofstream build_file((temp + jobs_path + 		     \
				    BUILD_OUTPUT_FILE).c_str(),
				    ios_base::app);
		build_file << "-1:  compilarea a produs " << build_c-1 <<    \
                                     " warning-uri" << endl;
		build_file.close();
	}


	/* write timeout in RUN_OUTPUT_FILE */
	ofstream run_file((temp+jobs_path+RUN_OUTPUT_FILE).c_str(),
			 ios_base::app);

	if (timeout < vmrun.timeout)
		run_file << "timeout=" <<vmrun.timeout-timeout;
	else
		run_file << "Tester timeouted";

	run_file.close();
	outfile.close();
	return 0;
}

/*--------------------------------------------------------------------------*/
/**
   This  function uses VIX API to power off the Virtual Machine.
*/
/*--------------------------------------------------------------------------*/
static int close_vm()
{
	log("[EXECUTOR] Closing VM...\n");
	jobHandle=VixVM_PowerOff(
			vmHandle,
			0,
			NULL,
			NULL);

	err=VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		log("[EXECUTOR] VixVM_PowerOff: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		return -1;
	}

	return 0;
}

/*--------------------------------------------------------------------------*/
/**
   This function starts listening to kernel messages.
*/
/*--------------------------------------------------------------------------*/
static int start_kernel_listener(void)
{
	string command;
	int fd;

	if (vmrun.vmname == "lin")
	{
		log("[EXECUTOR] Starting Netcat...\n");
		switch (pid_nc = fork())
		{
			case -1: /* fork failed */
				printf("fork failed\n");
				exit(EXIT_FAILURE);
				break;

			case 0: /* child starts executing here */
				fd = open(KMESSAGE_OUTPUT_FILE,
					  O_RDWR | O_CREAT, 0644);

				if (fd == -1)
					return -1;
				dup2(fd, STDOUT_FILENO);
				execlp("nc", "nc", "-u", "-l", "-p6666",
				       (char*)NULL);
				break;
		}
	}
	else
	{
		command = command + " --login -c \"dbgview /l " +		     \
			KMESSAGE_OUTPUT_FILE + " & sleep 3 && tail -f " +    \
			KMESSAGE_OUTPUT_FILE + " >> " +			     \
			KMESSAGE_OUTPUT_FILE + "\"";

		// run the target program.
		log("[EXECUTOR] Starting dbgview... shell=[%s] args[%s]\n", 
		    vmrun.guest_shell.c_str(), command.c_str());
		jobHandle = VixVM_RunProgramInGuest(
				vmHandle,
				vmrun.guest_shell.c_str(),
				command.c_str(),
				0,			// options,
				VIX_INVALID_HANDLE,	// propertyListHandle,
				NULL,			// callbackProc,
				NULL);			// clientData

		err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
		if (VIX_OK != err)
		{
			error("[EXECUTOR] VixVM_RunProgramInGuest: %s: %llu\n",
			      Vix_GetErrorText(err,NULL), err);
			error("[EXECUTOR] VixVM_RunProgramInGuest: guestshell=%s: commanad=%s\n",
			      vmrun.guest_shell.c_str(), command.c_str());
			return -1;
		}

	}

	return 0;
}

/*--------------------------------------------------------------------------*/
/**
  This function inspects the returning value of the command invoked by
  system() function.

  @param    str: the string to be modified
  @return   -1 if system() failed
            the returning code of the command invoked
*/
/*--------------------------------------------------------------------------*/

/*
static int system_return_value(int ret, const char* message)
{
	if (ret==-1)
	{
		error("\"system()\" failed\n");
		return -1;
	}
	else
	{
		if (WIFEXITED(ret))
        {
            if ((WEXITSTATUS(ret) != 0))
			{
				error("%s\n",message);
				return WEXITSTATUS(ret);
			}
			else
                return 0;
        }
	}

	return -1;
}
*/

/*--------------------------------------------------------------------------*/
/**
   This function runs a script which installs locally the CHECKER_TEST
*/
/*--------------------------------------------------------------------------*/

 /*
static int install_local_tests(void)
{
	string command;
	int ret;
	command += "unzip " + jobs_path + "/" + CHECKER_TEST + " -d " +      \
		jobs_path;

	ret = system (command.c_str());
	ret = system_return_value(ret, "Cannot unpack local tests");

	if (ret != 0) return -1;

	command = "";
	command = command + "bash --login -c \"" + "chmod +x " + jobs_path + "/"     \
		 + LOCAL_SCRIPT + ";" + jobs_path + "/" + LOCAL_SCRIPT+      \
		" " + "\'" + vmrun.local_ip + "\'" + " " + "\'" + 	     \
		vmrun.guest_ip + "\'" + "\"";

	ret = system(command.c_str());
	ret = system_return_value(ret, "Cannot run local script");

	return ret;
}
 */

/*--------------------------------------------------------------------------*/
/**
    This function is an emergency service.
*/
/*--------------------------------------------------------------------------*/
static void abort_job(int error_code)
{
	log("[EXECUTOR] Abort job\n");
	if (pid_nc != -1)
		kill(pid_nc, SIGTERM);

	if ( close_vm() != 0)
		exit(-1);

	Vix_ReleaseHandle(jobHandle);
	Vix_ReleaseHandle(snapshotHandle);
	Vix_ReleaseHandle(vmHandle);
	VixHost_Disconnect(hostHandle);

	exit(error_code);
}

/*--------------------------------------------------------------------------*/
/**
    This function prints the arguments this program should be passed.
*/
/*--------------------------------------------------------------------------*/
static void usage(char *argv0)
{
	fprintf(stderr, "Usage: %s vm_name(win|lin) enable_k_m(1|0)"
			" vmpath local_ip guest_user guest_pass "
			" guest_home guest_shell guest_home_in_shell"
			" root job_id\n", argv0);
}

/*--------------------------------------------------------------------------*/
/**
                      MAIN
*/
/*--------------------------------------------------------------------------*/
int main(int argc, char *argv[])
{
	//struct args_struct args;
	int ret;

	if (argc != 12)
	{
		usage(argv[0]);
		exit(EXIT_FAILURE);
	}

	if (fill_vmrun( argv) < 0) {
		fprintf(stderr, "Error parsing command line arguments.\n");
		exit(EXIT_FAILURE);
	}
	print_run();

	if ((ret = start_vm()) != 0)
		abort_job(ret);

	if (vmrun.km_enable)
	{
		log("[EXECUTOR] Start listening to kernel...\n");
		if ((ret = start_kernel_listener()) != 0)
			abort_job(ret);
	}

//	install_local_tests();

	if((ret = copy_files()) != 0)
		abort_job(ret);

	if ((ret = run_scripts()) != 0)
		abort_job(ret);

	if (pid_nc != -1)
		kill(pid_nc, SIGTERM);

	if (close_vm() != 0)
		exit(-1);

	Vix_ReleaseHandle(jobHandle);
	Vix_ReleaseHandle(snapshotHandle);
	Vix_ReleaseHandle(vmHandle);
	VixHost_Disconnect(hostHandle);

	return 0;
}
