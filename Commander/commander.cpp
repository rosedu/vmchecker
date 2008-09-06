/*
 * checker.cpp - VMware control program - uses VIX API
 *
 * (C) 2008 Adriana Szekeres <aaa_sz@yahoo.com>
 * coding issues, Razvan Deaconescu <razvan@rosedu.org>
 */

#include <iostream>
#include <fstream>
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

#include <vix.h>

using namespace std;

#include "debug.h"
#include "log.h"
#include "checker.h"

/* running information */
static struct run_struct vmrun;

/* define global variables */
static VixError err = VIX_OK;
static VixHandle hostHandle = VIX_INVALID_HANDLE;
static VixHandle jobHandle = VIX_INVALID_HANDLE;
static VixHandle vmHandle = VIX_INVALID_HANDLE;
static VixHandle snapshotHandle = VIX_INVALID_HANDLE;

static int snapshotIndex;
static int pid_nc = -1;

Bool jobCompleted;

/*
 * fill vmrun structure with virtual machine info from arguments  
 */

static int fill_vmrun( char **argv)
{
	char *endp;

	vmrun.vmname = argv[1];

	if (strcmp(argv[2], "0") != 0) {
		if (strcmp(argv[2], "1") != 0) {
			fprintf(stderr, "Usage error.\n");
			return -1;
		}
		else {
			vmrun.km_enable = true;
		}
	}
	else {
		vmrun.km_enable = false;
	}

	if (strptime(argv[3], "%Y-%m-%d %H:%M:%S", &vmrun.deadline_time) == NULL) {
		error("strptime failed\n");
		return -1;
	}
	if (strptime(argv[4], "%Y-%m-%d %H:%M:%S", &vmrun.upload_time) == NULL) {
		error("strptime failed\n");
		return -1;
	}

	vmrun.penalty = strtof(argv[5], &endp);
	vmrun.vmpath=argv[6];
	vmrun.local_ip=argv[7];
	vmrun.base="./";
	vmrun.guest_user=argv[8];
	vmrun.guest_pass=argv[9];
	vmrun.guest_home=argv[10];
	vmrun.guest_shell=argv[11];
	vmrun.guest_home_in_bash=argv[12];
	vmrun.build_command_args= vmrun.build_command_args+"-c \" chmod +x "+ vmrun.guest_home+ BUILD_SCRIPT+ ";"+vmrun.guest_home+BUILD_SCRIPT+" "+vmrun.vmname + " "+vmrun.guest_home_in_bash+" \"";
	vmrun.run_command_args=vmrun.run_command_args+ "-c \" chmod +x "+vmrun.guest_home+RUN_SCRIPT+";"+vmrun.guest_home+RUN_SCRIPT+" "+vmrun.vmname + " "+vmrun.guest_home_in_bash+" \"";	

	return 0;
}

/*
 * append content of infile to outfile
 * (similar to "cat infile >> outfile" shell command)
 */

static int append_f(const char *infile, const char *outfile, const char* message)
{
	string line;
	string oldline;
	ifstream in_file(infile);
	ofstream out_file(outfile, ios_base::app);

	if (!(in_file.is_open() && out_file.is_open()))
	{
		error("unable to open file %s or file %s\n", infile, outfile);
		in_file.close();
		out_file.close();
		return -1;
	
	}

	out_file << message << endl;

	while (!in_file.eof())
	{
		getline(in_file,line);
		out_file << line << endl; 
	}

	in_file.close();
	out_file.close();

	return 0;
}

static void print_run(void)
{
	cout << "=== Running job ===" << endl;
	cout << "vmname: " << vmrun.vmname << endl;
	cout << "vmdesc: " << vmrun.vmdesc << endl;
	cout << "guest_user: " << vmrun.guest_user << endl;
	cout << "guest_pass: " << vmrun.guest_pass << endl;
	cout << "guest_home: " << vmrun.guest_home << endl;
	cout << "guest_shell: " << vmrun.guest_shell << endl;
	cout << "guest_ip: " << vmrun.guest_ip << endl;
	cout << "build_command_args: " << vmrun.build_command_args << endl;
	cout << "run_command_args: " << vmrun.run_command_args << endl;
	cout << "upload_time: " << asctime(&vmrun.upload_time);
	cout << "deadline_time: " << asctime(&vmrun.deadline_time);
	cout << "penalty: " << vmrun.penalty << endl;
	cout << "km_enable: " << (vmrun.km_enable == true ? "true" : "false") << endl;
	cout << "===================" << endl;
}

/*
 * get virtual machine IP address from BUILD_OUTPUT_FILE
 */

static int get_vm_ip()
{
	string line;
	ifstream infile(BUILD_OUTPUT_FILE);

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

/* 
 * check build on guest system (virtual machine)
 * return value
 *   -1 if a system error occurs
 *    0 for "checker: building failed"
 *    [warning_count+1] for "checker: building done" 
 */

static int check_build(void)
{
	string line;
	string oldline;
	ifstream infile(BUILD_OUTPUT_FILE);

	int warning_count = 0;

	if (!infile.is_open())
	{
		error("unable to open file %s\n",
				BUILD_OUTPUT_FILE);
		return -1;
	}	

	while (!infile.eof())
	{
		getline(infile,line);

		if(line.find("checker: building") != string::npos)
			break;
	}

	if (infile.eof())
	{ 
		infile.close();
		return -1;
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

	return warning_count+1;
}

/*
 * returns the number of days between upload_date and deadline_date
 * if upload_date>deadline, else 0 
 */

static int check_deadline(void)
{

	double secs;
	int days;

	secs = difftime(mktime(&vmrun.upload_time),
			mktime(&vmrun.deadline_time));
	days = secs / 60 / 60 / 24;

	if (secs < 0)
		return 0;
		
	if (days > 12)
		days = 12;
	
	return days;
}

/*
 * checks for bugs in file KMESSAGE_OUTPUT_FILE
 * returns number of bugs
 */

static int check_bugs(void)
{
	string line;
	ifstream infile(KMESSAGE_OUTPUT_FILE);
	
	int bugs_count = 0;

	if (!infile.is_open())
	{
		error("unable to open file %s\n", KMESSAGE_OUTPUT_FILE);
		return -1;
	}	

	while (!infile.eof())
	{
		getline(infile,line);

		if(line.find("BUG:") != string::npos)
			bugs_count++;
	}
	
	infile.close();

	return bugs_count;
}

/*
 * start guest operating system (use VIX API)
 */

static int start_vm(void)
{
	log("Connecting to server...\n");
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
   		error("VixHost_Connect: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
   		return -1;
	}

	Vix_ReleaseHandle(jobHandle);
 
	log("Opening VM...\n");
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
		error("VixVM_Open: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err); 
		return -1;
	}

	Vix_ReleaseHandle(jobHandle);

	log("Getting SnapShot...\n");

	// revert to snapshot #0
	snapshotIndex = 0;
	err = VixVM_GetRootSnapshot(
			vmHandle,
			snapshotIndex,
			&snapshotHandle);
	if (VIX_OK != err)
	{
		error("VixVM_GetRootSnapshot: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
   		return -1;
	}

	log("Reverting to SnapShot...\n");
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
		error("VixVM_RevertToSnapshot: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		return -1;
	}

	log("Waiting for Tools...\n");

	// wait until guest completes bootup process
	while (1) {
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
				log("Retrying Waiting for Tools...\n");
				continue;
			}

			error("VixVM_WaitForToolsInGuest: %s: %llu\n",
					Vix_GetErrorText(err,NULL), err);
			return -1;
		}

		break;
	}

	log("Logging in...\n");

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
		error("VixVM_LoginInGuest: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		return -1;
	}

	return 0;
}

/*
 * copy necesary files to guest OS
 */

static int copy_files(void)
{
	// copy checker archive
	log("Copying %s...\n", CHECKER_FILE);

	jobHandle = VixVM_CopyFileFromHostToGuest(
			vmHandle,
			(vmrun.base + CHECKER_FILE).c_str(),
			(vmrun.guest_home + CHECKER_FILE).c_str(),
			0,				// options
			VIX_INVALID_HANDLE,		// propertyListHandle
			NULL,				// callbackProc
			NULL);				// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("VixVM_CopyFileFromHostToGuest: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		return -1;
	}

	// copy CHECKER_TEST.zip
	log("Copying %s...\n", CHECKER_TEST);
	jobHandle = VixVM_CopyFileFromHostToGuest(
			vmHandle,
			(vmrun.base + CHECKER_TEST).c_str(),
			(vmrun.guest_home + CHECKER_TEST).c_str(),
			0,				// options
			VIX_INVALID_HANDLE,		// propertyListHandle
			NULL,				// callbackProc
			NULL);				// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("VixVM_CopyFileFromHostToGuest: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		return -1;
	}

        // copy build script
	log("Copying %s...\n", BUILD_SCRIPT);
	jobHandle = VixVM_CopyFileFromHostToGuest(
			vmHandle,
			(vmrun.base + BUILD_SCRIPT).c_str(),
			(vmrun.guest_home + BUILD_SCRIPT).c_str(),
			0,				// options
			VIX_INVALID_HANDLE,		// propertyListHandle
			NULL,				// callbackProc
			NULL);				// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("VixVM_CopyFileFromHostToGuest: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		return -1;
	}

	// copy running script
	log("Copying %s...\n", RUN_SCRIPT);
	jobHandle = VixVM_CopyFileFromHostToGuest(
			vmHandle,
			(vmrun.base + RUN_SCRIPT).c_str(),
			(vmrun.guest_home + RUN_SCRIPT).c_str(),
			0,				// options
			VIX_INVALID_HANDLE,		// propertyListHandle
			NULL,				// callbackProc
			NULL);				// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		error("VixVM_CopyFileFromHostToGuest: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		return -1;
	}

	return 0;
}

/*
 * handler function for SIGALRM
 */

void alarm_handler(int sig)
{
	/* do nothing; succesfully */
}

/*
 * set signal
 */

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

/*
 * Callback function for RunProgramInGuest
 */

static void run_cb(VixHandle jobHandle, VixEventType eventType,
		VixHandle eventInfo, void* clientData)
{
	alarm(1);
}

/*
 * run build and running scripts in guest OS
 */

static int run_scripts(void)
{
	int build_c = 0;
	int bugs_c = 0;
	int deadline_c = 0;
	int timeout;

	ofstream outfile(RESULT_OUTPUT_FILE);
	
	if (!outfile.is_open())
	{
		error("unable to open file %s\n", RESULT_OUTPUT_FILE);
		return -1;
	}

	// run the target program. 
	log("Starting %s...\n", BUILD_SCRIPT);
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
		return -1;
	}

	
	// get BUILD_OUTPUT_FILE
	log("Fetching %s...\n", BUILD_OUTPUT_FILE);
	jobHandle = VixVM_CopyFileFromGuestToHost(
			vmHandle,
			(vmrun.guest_home + BUILD_OUTPUT_FILE).c_str(),
			(vmrun.base + BUILD_OUTPUT_FILE).c_str(),
			0,			// options
			VIX_INVALID_HANDLE,	// propertyListHandle
			NULL,			// callbackProc
			NULL);			// clientData
	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
                error("VixVM_CopyFileFromGuestToHost: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		return -1;
	}

	//check if build succesful
	build_c = check_build();
	if (build_c == -1)
	{
		error("System error: check_build failed\n");
		return -1;
	}
	else
	{
		if (build_c == 0)
		{
			outfile << "0\n" << endl;
			outfile << "-10: tema nu se compileaza" << endl;
			outfile.close();
			append_f(BUILD_OUTPUT_FILE, RESULT_OUTPUT_FILE, "\nBUILD RESULTS:\n");
			return -1;
		}
	}

	//get_vm_ip
	if (get_vm_ip() == -1)
	{
		error("System error: get_vm_ip failed\n");
		return -1;
	}

	log("VM's IP = %s\n", vmrun.guest_ip.c_str());

	//build succesful, go on with runnig CHECKER_TEST

	/* setup alarm signal to be sent after 120 seconds */
	set_signal();
	alarm(120);

	// run the target program. 
	log("Starting %s...\n", RUN_SCRIPT);
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

	// get RUN_OUTPUT_FILE
	log("Fetching %s...\n", RUN_OUTPUT_FILE);
	jobHandle = VixVM_CopyFileFromGuestToHost(
			vmHandle,
			(vmrun.guest_home + RUN_OUTPUT_FILE).c_str(),
			(vmrun.base + RUN_OUTPUT_FILE).c_str(),
			0,				// options
			VIX_INVALID_HANDLE,		// propertyListHandle
			NULL,				// callbackProc
			NULL);				// clientData

	err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
                error("VixVM_CopyFileFromGuestToHost: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		return -1;
	}

	//if kernel messages enabled, fetch KMESSAGE_OUTPUT_FILE
	if (vmrun.km_enable)
	{
		log("Fetching %s...\n", KMESSAGE_OUTPUT_FILE);	
		if (vmrun.vmname == "win")
		{
			jobHandle = VixVM_CopyFileFromGuestToHost(
				vmHandle,
				(vmrun.guest_home + KMESSAGE_OUTPUT_FILE).c_str(),
				(vmrun.base + KMESSAGE_OUTPUT_FILE).c_str(),
				0,				// options
				VIX_INVALID_HANDLE,		// propertyListHandle
				NULL,				// callbackProc
				NULL);				// clientData

			err = VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
			if (VIX_OK != err)
			{
				error("VixVM_CopyFileFromGuestToHost: %s: %llu\n",
						Vix_GetErrorText(err,NULL), err);
				return -1;
			}
		}

		bugs_c = check_bugs();
		if (bugs_c == -1)
		{
			error("System error: check_bugs failed\n");
			return -1;
		}
	}

	if (bugs_c > 0)
	{
		outfile << "0\n" << endl;
		outfile << "-10: au fost identificate " << bugs_c << " bug-uri" << endl;
	}
	else
		outfile << "ok\n" << endl;

	if(build_c > 1)
		outfile << "-1:  compilarea a produs " << build_c-1 << " warning-uri" << endl;

	deadline_c = check_deadline();
	if (deadline_c == -1)
		error("System error: check_deadline failed\n"); //but go on?

	if (deadline_c > 0)
		outfile << "-" << deadline_c*vmrun.penalty / 100.0 <<": intarziere " <<deadline_c << " zile" << endl;

	outfile.close();

	append_f(BUILD_OUTPUT_FILE, RESULT_OUTPUT_FILE, "\nBUILD RESULTS:\n");
	append_f(RUN_OUTPUT_FILE, RESULT_OUTPUT_FILE, "\nRUN RESULTS:\n");

	if (vmrun.km_enable)
		append_f(KMESSAGE_OUTPUT_FILE, RESULT_OUTPUT_FILE,
				"\nKERNEL MESSAGES:\n");

	log("timeout = %d\n", timeout);

	return 0;
}

/*
 * close virtual machine
 */

static int close_vm()
{
/*	log("Closing VM...\n");
	jobHandle=VixVM_PowerOff(
			vmHandle,
			0,
			NULL,
			NULL);

	err=VixJob_Wait(jobHandle, VIX_PROPERTY_NONE);
	if (VIX_OK != err)
	{
		log("VixVM_PowerOff: %s: %llu\n",
				Vix_GetErrorText(err,NULL), err);
		return -1;
	}
*/
	return 0;
}

/*
 *  starts listening to kernel messages - uses netconsole
 */

static int start_kernel_listener(void)
{
	string command;
	int fd;

	if (vmrun.vmname == "lin")
	{
		switch (pid_nc = fork())
		{
			case -1: /* fork failed */
				printf("fork failed\n");
				exit(EXIT_FAILURE);
				break;

			case 0: /* child starts executing here */
				fd = open(KMESSAGE_OUTPUT_FILE, O_RDWR | O_CREAT, 0644);

				if (fd == -1)
					return -1;
				dup2(fd, STDOUT_FILENO);

				execlp("nc", "nc", "-u", "-l", "-p6666", (char*)NULL);
				break;
		}
	}
	else
	{
		command = command + "-c \"dbgview /l " +
			KMESSAGE_OUTPUT_FILE + " & sleep 3 && tail -f " +
			KMESSAGE_OUTPUT_FILE + " >> " +
			KMESSAGE_OUTPUT_FILE + "\"";  

		// run the target program. 
		log("Starting dbgview...\n");
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
			error("VixVM_RunProgramInGuest: %s: %llu\n",
					Vix_GetErrorText(err,NULL), err);
			return -1;
		}
	
	}

	return 0;
}

/*
 * runs a script which installs localy the CHECKER_TEST
 */

static void install_local_tests(void)
{
	string command;
	
	command = command +vmrun.base  + LOCAL_SCRIPT + " " + vmrun.local_ip + " " + vmrun.guest_ip;
	system(command.c_str());
}

/*
 * abort function
 */

static void abort_job()
{
	if (pid_nc != -1)
		kill(pid_nc, SIGTERM);

	close_vm();
	Vix_ReleaseHandle(jobHandle);
	Vix_ReleaseHandle(snapshotHandle);
	Vix_ReleaseHandle(vmHandle);
	VixHost_Disconnect(hostHandle);
	
	exit(EXIT_FAILURE);
}

/*
 * print usage
 */

static void usage(char *argv0)
{
	fprintf(stderr, "Usage: %s vm_name(win|lin) enable_k_m(1|0)"
			" deadline upload_date penalty(25)"
			"vmpath local_ip guest_user guest_pass guest_home guest_shell guest_home_in_shell\n", argv0);
}

/*
 * main function
 */

int main(int argc, char *argv[])
{
	//struct args_struct args;

	if (argc != 13)
	{
		usage(argv[0]);
		exit(EXIT_FAILURE);
	}

	if (fill_vmrun( argv) < 0) {
		fprintf(stderr, "Error parsing command line arguments.\n");
		exit(EXIT_FAILURE);
	}
	print_run();

/*	config = read_config(CHECKER_CONFIG);
	if (config == NULL)
	{
		fprintf(stderr, "Error in configuration file.\n");
		exit(EXIT_FAILURE);
	}

	define_run(config, &args);
	print_run();
*/
	if (start_vm() != 0)
		abort_job();

	if (vmrun.km_enable)
	{
		log("Start listening messages from kernel...\n");
		if (start_kernel_listener() != 0)
			abort_job();
	}

//	install_local_tests();

	if(copy_files() != 0)
		abort_job();

	if (run_scripts() != 0)
		abort_job();

	if (pid_nc != -1)
		kill(pid_nc, SIGTERM);

	close_vm();

	Vix_ReleaseHandle(jobHandle);
	Vix_ReleaseHandle(snapshotHandle);
	Vix_ReleaseHandle(vmHandle);
	VixHost_Disconnect(hostHandle);

	return 0;
}
