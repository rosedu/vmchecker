/*------------------------- 78 characters line -----------------------------*/
/*----------------------- NO BIGGER LINES ALLOWED :D -----------------------*/
/**
   @file	commander.cpp
   @author	Adriana Szekeres <aaa_sz@yahoo.com>
   @date	September 2008
   @version	Version 1.0 Release 1
   @brief	Commands VMExecutor - using iniparser3.0b

   Coding issues, Alexandru Mosoi <brtzsnr@gmail.com>

      This module copies from Uploader System  the two archives (file.zip and 
   tests.zip),  parses  the  two  configuration   files    (vm_config.ini and 
   homework.ini,  described in  the documentation file) and starts VMExecutor 
   (bin/vm_executor) accordingly.
*/
/*--------------------------------------------------------------------------*/

#include <stdio.h>
#include <fstream>
#include <iostream>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <unistd.h>
#include <cstdarg>
#include <assert.h>
#include <time.h>

#include "log.h"
#include "commander.h"

#include <fcntl.h>
#include <sys/wait.h>

extern "C" {
#include "iniparser.h"
}

using std::cout;
using std::fstream;
using std::cerr;
using std::string;
using std::ios;
using std::ifstream;
using std::ofstream;
using std::endl;

/*--------------------------------------------------------------------------*/
/*--------------------- Global Variables -----------------------------------*/
static char* vmchecker_root;		/* course root */
static char* vmchecker_root_local;	/* local course root */ 
static char* vm_name;			/* virtual machine's name */
static char* username;			/* tester system's username */
static char* ip;			/* upload system's ip address */
static char* job_id;			/* homework's name */
static char* user_id;			/* student's name */
static char* deadline;			/* homework's deadline */
static char* upload_time;		/* homework's upload time */
static char* penalty_script;		/* path to penalty script */ 
static char* kernel_msg;		/* kernel messages enable */
static char* local_ip;			/* tester system's IP address */
static char* vm_path;			/* path to vm's configuration file */
static char* guest_user;		/* vm's username */
static char* guest_pass;		/* vm's password */	
static char* guest_base_path;		/* path to vm's working
                                        directory (home directory) */
static char* guest_shell_path;		/* path to vm's shell */
static char* guest_home_in_bash;	/* path to working directory in
					shell (used for cd command in build/
					run.sh) */

static const char* jobs_path;		/*path to temporary working files
					for executor */

static	dictionary* instance; 		/* homework.ini */
static	dictionary* v_machines; 	/* vm_config.ini */
/*--------------------------------------------------------------------------*/

/*--------------------- Functions code -------------------------------------*/
/*--------------------------------------------------------------------------*/
/**
  This function concatenates multiple char arrays into one string.

  @param    arg_n: multiple char arrays
  @return   A string representing the concatenation of all arguments
*/
/*--------------------------------------------------------------------------*/
static string concatenate(const char* arg1,... )
{
	va_list arguments;
	va_start(arguments, arg1);

	string temp;
	const char* str = arg1;

	for (; str != NULL; str = va_arg(arguments, const char*))
		temp += str;

	va_end(arguments);	
	//cerr << "concatenate: " << temp << endl;
	return temp;
}

static int echo_system(const char* command) {
	cout << command << endl;
	return system(command);
}

#define system(command) echo_system(command)

/*--------------------------------------------------------------------------*/
/**
  This function modifies the input string by replacing spaces with "\ ".

  @param    str: the string to be modified
  @return   A string that replaces " " by "\ " in str

*/
/*--------------------------------------------------------------------------*/
static string escape(const string& path) {
	string aux;

	const char* str = path.c_str();
	for (; *str != 0; str++) 
	{
		// escapes only spaces.
		if (isblank(*str))
			aux.push_back('\\');
		aux.push_back(*str);
	}

	return aux;
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
static int system_return_value(int ret)
{
	if (ret == -1)
	{
		error("ERROR: \"system()\" failed\n");
		return -1;
	}
	else
	{	
		if (WIFEXITED(ret))
		{
			if ((WEXITSTATUS(ret) != 0))
			{
			return WEXITSTATUS(ret);
			}
			else return 0;
		}
	}

	return -1;
}

/*--------------------------------------------------------------------------*/
/**
  This function clears "executor_jobs" directory.

  @return   the returning code of system_return_value()
            - see previous function 

*/
/*--------------------------------------------------------------------------*/
static int clear_jobs_dir()
{
	string temp;
	int ret;

	temp = concatenate ("rm -rf ", escape(jobs_path).c_str(), \
                            "/*", NULL);
	ret = system_return_value (system (temp.c_str()));
	
	if (ret != 0)
		cout << "Cannot clear executor_jobs directory" << endl;
	return ret;
}


/*--------------------------------------------------------------------------*/
/**
  This function frees the two global dictionaries used for parsing the two
  ini files.
*/
/*--------------------------------------------------------------------------*/
void free_resources()
{
	iniparser_freedict (instance);
	iniparser_freedict (v_machines);
}

/*--------------------------------------------------------------------------*/
/**
  This function frees the two global dictionaries used for parsing the two
  ini files and clears "executor_jobs" directory. It is called in case of 
  failure.

  @return  exits with -1
*/
/*--------------------------------------------------------------------------*/
void abort_job()
{
	free_resources();
	clear_jobs_dir();
	exit(-1);
}

/*--------------------------------------------------------------------------*/
/**
  This function extracts a file name from a global path.

  @param   conf : the path to the file 
  @return  A char array representing the configuration file's name
*/
/*--------------------------------------------------------------------------*/
char* conf_file(char conf[])
{
	char* a1;
	char* a2;
		for(a1 = strtok(conf,"/"); a1 != NULL; a1 = strtok(NULL,"/"))
	{
		a2 = a1;
	}
	return a2;
}

/*--------------------------------------------------------------------------*/
/**
  This function uses scp command to copy files from a system having the 
  IP address specified in "ip" argument and the username specified in 
  "username" argument.

  @param   ip : uploading system's IP address
  @param   username : uploading system's loggin-in username
  @param   dest : path to destination
  @param   src :  path to source 
*/
/*--------------------------------------------------------------------------*/
static int copy_from_uploader(const char* username, const char* ip, \
		       const string& src, const string& dest)
{
	int ret;
	string temp;

	temp += concatenate("scp", " ", NULL);
	temp += concatenate(username, "@", ip, ":\"", \
                            escape(src).c_str(), "\" ", NULL);
	temp += concatenate("\"", escape(dest).c_str(), "\" ", NULL);
	temp += "> /dev/null";
	cout <<  "[COMMANDER] " << temp << endl;

	ret = system_return_value(system(temp.c_str()));

	if (ret != 0)
		cout << "[COMMANDER] Cannot get file : " << src \
                     << " from Upload System " << endl; 
	return ret;		
}

/*--------------------------------------------------------------------------*/
/**
  This function uses scp command to copy files to a system having the 
  IP address specified in "ip" argument and the username specified in 
  "username" argument. Is *space-escapes* "dest" and "src".

  space_escaped means that spaces are replaced by "\ "

  @param   ip : uploading system's IP address
  @param   username : uploading system's loggin-in username
  @param   dest : path to destination
  @param   src :  path to source 
*/
/*--------------------------------------------------------------------------*/
static int copy_to_uploader(const char* username, const char* ip, \
			    const string& src, const string& dest)
{
	int ret;
	string temp;

	temp += concatenate("scp", " ", NULL);
	temp += concatenate("\"", escape(src).c_str(), "\" ", NULL);
	temp += concatenate(username, "@", ip, ":\"", \
			    escape(dest).c_str(), "\"", NULL);
	temp += "> /dev/null";
	cout << "[COMMANDER] " << temp << endl;
	ret = system_return_value(system(temp.c_str()));

	if (ret != 0)
		cout << "[COMMANDER] Cannot upload file : " << src \
		     << " to Upload System " << endl; 
	return ret;		
}

/*--------------------------------------------------------------------------*/
/**
  This  function  executes  a  ssh  command  on the remote system having the 
  IP address specified  in "ip"  argument  and  the  username  specified  in 
  "username"  argument. This function should  be used knowing that the first
  argument  after  "ip"  isn't  *space_escaped*  (assumed  it  is  a command 
  - with options - ; if it is not a command  the function  should be  called
  with  an extra space  as first argument);  the  second argument after "ip"
  is space_escaped, the third is not, and so on... .   

  space_escaped means that spaces are replaced by "\ "

  @param   ip : uploading system's IP address
  @param   username : uploading system's loggin-in username
  @param   arg_n : multiple string arrays
*/
/*--------------------------------------------------------------------------*/
int ssh_command(const char* username, const char* ip, ...)
{
	va_list arguments;
	va_start(arguments, ip);
	string temp;
	int ret=0;
	const char* str = va_arg(arguments, const char*);

	temp += concatenate("ssh", " ", username, "@", ip, " ", "\"", NULL);
	for (; str != NULL; str = va_arg(arguments, const char*))
	{
		temp += str;
		str = va_arg(arguments, const char*);
		if (str != NULL)
			temp += escape(str);
		else break;
	}
	temp += "\"";
	cout << "[COMMANDER] " << temp << endl; 
	ret = system_return_value(system(temp.c_str()));

	if (ret != 0)
		cout << "[COMMANDER] Cannot execute ssh command: " << temp << endl; 
	va_end(arguments);	
	return ret;		
}

/*--------------------------------------------------------------------------*/
/**
  This  function appends "infile" to "outfile" . 
  (similar to "cat infile >> outfile" shell command)
  
  @param   infile : path to the file to be appended
  @param   outfile : path to the file to be written
  @param   message : message to be written in outfile before appending infile
*/
/*--------------------------------------------------------------------------*/
static int append_f(const char *infile, const char *outfile,                 \
		    const char* message)
{
	string line;
	string oldline;
	ifstream in_file(infile);
	ofstream out_file(outfile, ios::app);

	if (!(in_file.is_open() && out_file.is_open()))
	{
		error("unable to open file %s or file %s\n",                 \
                                                 infile, outfile);
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

/*--------------------------------------------------------------------------*/
/**
  This function checks for string "BUG:" in a file. It is used for checking
  for reported bugs in kernel messages. 

  @return  number of bugs found
           -1 in case of failure
*/
/*--------------------------------------------------------------------------*/
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


/*--------------------------------------------------------------------------*/
/**
  This function parses two .ini files and extracts the necessary global
  information.

  @param  ini_instance path to a .ini file
  @param  ini_v_machines path to a .ini file
*/
/*--------------------------------------------------------------------------*/
static void parse_ini_files(const char *ini_instance, 			     \
			    const char* ini_v_machines)
{
	string temp;
	
	instance = iniparser_load (ini_instance);
	if (instance == NULL)
	{
		error("Cannot parse file: %s\n", ini_instance);
		exit(-1) ;
	}

	v_machines=iniparser_load (ini_v_machines);
	if (v_machines == NULL)
	{
		error("Cannot parse file: %s\n", ini_v_machines);
		exit(-1);
	}


	//iniparser_dump(instance, stderr);
	//iniparser_dump(v_machines,stderr);

	/* extracting homework info */
	vmchecker_root = iniparser_getstring(instance, 			     \
						"DEFAULT:VMCheckerRoot",NULL);
	assert (vmchecker_root != NULL);
	vm_name = iniparser_getstring(instance, "DEFAULT:VMName",NULL);
	assert (vm_name != NULL);
	job_id = iniparser_getstring(instance, "DEFAULT:Job",NULL);
	assert (job_id != NULL);
	user_id = iniparser_getstring(instance, "DEFAULT:UserId",NULL);
	assert (user_id != NULL);
	deadline = iniparser_getstring(instance, "DEFAULT:Deadline",NULL);
	assert (deadline !=NULL);
	upload_time = iniparser_getstring(instance,"DEFAULT:UploadTime",NULL);
	assert (upload_time != NULL);
	penalty_script = iniparser_getstring(instance, 			     \
                                                "DEFAULT:PenaltyScript",NULL);
	assert (penalty_script != NULL);
	kernel_msg = iniparser_getstring(instance, "DEFAULT:KernelMsg",NULL);
	assert (kernel_msg != NULL);
	ip = iniparser_getstring(instance, "DEFAULT:UploaderIP",NULL);
	assert (ip != NULL);
	username = iniparser_getstring(instance, "DEFAULT:UploaderUsername", \
								        NULL);
	assert (username != NULL);
	

	temp = temp + vmchecker_root_local + "/executor_jobs/";
	jobs_path = strdup(temp.c_str());

	temp=vm_name;

	/*extracting vm info */ 
	local_ip = iniparser_getstring(v_machines,"Global:LocalAddress",NULL);
	assert (local_ip != NULL);
	vm_path = iniparser_getstring(v_machines,			     \
					     (temp + ":VMPath").c_str(),NULL);
	assert (vm_path != NULL);
	guest_user = iniparser_getstring(v_machines,  			     \
					  (temp + ":GuestUser").c_str(),NULL);
	assert (guest_user != NULL);
	guest_pass = iniparser_getstring(v_machines, 			     \
			 	      (temp + ":GuestPassword").c_str(),NULL);
	assert (guest_pass != NULL);
	guest_base_path = iniparser_getstring(v_machines, 		     \
				      (temp + ":GuestBasePath").c_str(),NULL);
	assert (guest_base_path != NULL);
	guest_shell_path = iniparser_getstring(v_machines, 		     \
				     (temp + ":GuestShellPath").c_str(),NULL);
	assert (guest_shell_path != NULL);
	guest_home_in_bash = iniparser_getstring(v_machines, 		     \
		                    (temp + ":GuestHomeInBash").c_str(),NULL);
	assert (guest_home_in_bash != NULL);
}


/*--------------------------------------------------------------------------*/
/**
  This function copies the two archives from Uploader.
*/
/*--------------------------------------------------------------------------*/
static int get_archives()
{
	string temp;
	int ret;

	//get CHECKER_FILE
	ret = copy_from_uploader(
		username, ip,
		concatenate(vmchecker_root, "/back/", job_id, "/", user_id,  \
			 "/", upload_time, "/", CHECKER_FILE, NULL),
		concatenate(jobs_path, "/", CHECKER_FILE, NULL));
	if (ret != 0)
		return ret;

	//get CHECKER_TEST
	ret = copy_from_uploader(
		username, ip,
		concatenate(vmchecker_root, "/tests/", job_id, ".zip", NULL),
		concatenate(jobs_path, "/", CHECKER_TEST, NULL));

	return ret;
}


/*--------------------------------------------------------------------------*/
/**
  This function starts VMExecutor.
*/
/*--------------------------------------------------------------------------*/
int start_executor()
{
	string temp="bash -c \"";
	int ret;	

	/* TODO: apelat cu >> vm_executor.log*/

	cout << "[COMMANDER] Starting executor" << endl;
	temp = concatenate ("bash -c \"", escape(vmchecker_root_local        \
			).c_str(), "/VMExecutor/", "vm_executor", " ",       \
			"\'", vm_name,"\' \'", kernel_msg, "\' \'", 	     \
			vm_path, "\' \'", local_ip, "\' \'",		     \
			guest_user, "\' \'", guest_pass, "\' \'",            \
			escape(guest_base_path).c_str(), "\' \'",	     \
			escape(guest_shell_path).c_str(), "\' \'",	     \
			escape(guest_home_in_bash).c_str(), "\' \'",	     \
			escape(vmchecker_root_local).c_str(), "\' \'", 	     \
			escape(job_id).c_str(), "\' \"", NULL);

	ret = system_return_value (system (temp.c_str()));

	if (ret != 0)
		cout << "[COMMANDER] ERROR: VMExecutor failed" << endl;	
	return ret;
}


/*--------------------------------------------------------------------------*/
/**
  This function clears "results" directory on Uploader System
  and creates "archive" directory. The archive directory will contain 
  the unziped file "file.zip". 
*/
/*--------------------------------------------------------------------------*/
int prepare_for_results_upload()
{
	int ret;

	ret = ssh_command(
		username, ip,
		"rm -rf ",
		concatenate(vmchecker_root, "/checked/", job_id,  "/",       \
				user_id, "/*", NULL).c_str(), 
		NULL);	
	
	if (ret != 0)
		return ret;
	
	ret = ssh_command(
		username, ip,
		"mkdir -p ",
		concatenate(vmchecker_root, "/checked/", job_id,  "/",       \
				user_id, "/archive", NULL).c_str(), 
		NULL);	
	
	return ret;
}



/*--------------------------------------------------------------------------*/
/**
  This function verifies and copies the results on Uploader.  
*/
/*--------------------------------------------------------------------------*/
static int upload_results()
{
	string temp;
	int ret,bugs_c;
	string first_line;

	if (prepare_for_results_upload() !=0)
		return -1;

	//read first line in RESULT_OUTPUT_FILE "0"/"ok" 
	fstream results_file;
	temp="";
	results_file.open((temp + jobs_path + RESULT_OUTPUT_FILE).c_str(),   \
								   ios::in);

	if (!results_file.is_open())
	{
		error("unable to open file %s\n", RESULT_OUTPUT_FILE);
		return -1;
	}

	getline(results_file,first_line);
	results_file.close();
	
	if (first_line == "0") //homework doesn't compile
	{
		append_f((temp + jobs_path + BUILD_OUTPUT_FILE).c_str(),     \
			(temp + jobs_path + RESULT_OUTPUT_FILE).c_str(),     \
			"\n     ===== BUILD RESULTS =====\n");
	}
	else
	{

		//check deadline 
		
		temp = concatenate(escape(vmchecker_root_local).c_str(), "/",\
		escape(penalty_script).c_str()," \'",\
		upload_time, "\' \'", deadline, "\' >> ",\
		escape(concatenate(jobs_path,\
		"/", RESULT_OUTPUT_FILE, NULL)).c_str(), NULL); 
		
		cout <<"[COMMANDER] Checking deadline\n" << temp << endl;
		
		ret = system(temp.c_str());
		ret = system_return_value(ret);

		if (ret != 0) 
			error("%s","Cannot check deadline");

		//but go on? 		
		temp="";		
		append_f((temp + jobs_path + BUILD_OUTPUT_FILE).c_str(),     \
			(temp + jobs_path + RESULT_OUTPUT_FILE).c_str(),     \
			"\n     ===== BUILD RESULTS =====\n");

		if (atoi(kernel_msg))
		{
			bugs_c = check_bugs();
	
			if (bugs_c == -1)
			{
				error("System error: check_bugs failed\n");
				return -1;
			}
			results_file.open((temp+jobs_path + 		     \
				RESULT_OUTPUT_FILE).c_str(),		     \
				ios::trunc);
	
			if (bugs_c > 0)
			{
				results_file << "0\n" << endl;
				results_file << "-10: au fost identificate " \
					     << bugs_c << " bug-uri" << endl;
				return -1;
			}
	
			results_file.close();
			append_f((temp + jobs_path +           		     \
				KMESSAGE_OUTPUT_FILE).c_str(), 		     \
				 (temp + jobs_path +           		     \
				RESULT_OUTPUT_FILE).c_str(),   		     \
			        "\n     ===== KERNEL MESSAGES =====\n");
	
		}
		append_f((temp + jobs_path + RUN_OUTPUT_FILE).c_str(),       \
			(temp + jobs_path + RESULT_OUTPUT_FILE).c_str(),     \
			"\n     ===== RUN RESULTS =====\n");
	}

	
	//upload RESULT_OUTPUT_FILE
	ret = copy_to_uploader(
		username, ip,
		concatenate(jobs_path, "/", RESULT_OUTPUT_FILE, NULL),
		concatenate(vmchecker_root, "/checked/", job_id, "/",        \
			    user_id, "/", "nota", NULL));

	
	if (ret != 0) return ret;

	cout << "[COMMANDER] Update note" << endl;

        ret = ssh_command(
		username, ip,
		concatenate(
			"export VMCHECKER_ROOT=", vmchecker_root, " && ",
			"cd $VMCHECKER_ROOT/checked", " && ",
			vmchecker_root, "/bin/update_db.py", " && ",
			vmchecker_root, "/bin/view_grades.py", " > $VMCHECKER_ROOT/checked/Note.html", NULL).c_str(),
		NULL);


	return ret;

}


/*--------------------------------------------------------------------------*/
/**
  This function copies and unzips homework archive (file.zip) on Uploader for
  further verification. 
*/
/*--------------------------------------------------------------------------*/
static int unzip_homework()
{
	string temp;
	int ret;

	ret = copy_to_uploader(						     \
		username, ip,						     \
		concatenate(jobs_path, "/",CHECKER_FILE, NULL), 	     \
		concatenate(vmchecker_root, "/checked/", job_id, "/",        \
			    user_id, "/archive/", NULL));

	if (ret != 0)
		return ret;

	ret = ssh_command(						     \
		username, ip,						     \
		"unzip ",						     \
		concatenate(vmchecker_root, "/checked/", job_id, "/",        \
			    user_id, "/archive/", CHECKER_FILE, 	     \
			    NULL).c_str(),				     \
			    " -d ",					     \
		concatenate(vmchecker_root, "/checked/", job_id, "/",        \
			    user_id, "/archive/", NULL).c_str(),	     \
		NULL);

	if (ret != 0)
		return ret;

	ret = ssh_command(						     \
		username, ip,						     \
		"rm -f ",						     \
		concatenate(vmchecker_root, "/checked/", job_id,  "/",       \
			    user_id, "/archive/", CHECKER_FILE, 	     \
			    NULL).c_str(),				     \
		NULL);	

	return ret;
}


/*--------------------------------------------------------------------------*/
/**
  This function removes homework configuration file from Tester and Uploader. 
*/
/*--------------------------------------------------------------------------*/
int remove_config_file(char* ini_instance)
{
	string temp;
	int ret;

	temp = concatenate ("rm -f ", escape(ini_instance).c_str(), NULL);
	cout << "[COMMANDER] " << temp << endl; 
	ret = system_return_value (system (temp.c_str()));

	if (ret != 0) 
		cout << "[COMMANDER] Cannot remove config file from Tester "
		     << "System"  << endl;

	ret = ssh_command(						     \
		username, ip,						     \
		"rm -f ",						     \
		concatenate(vmchecker_root, "/unchecked/", 		     \
			    conf_file(ini_instance) , NULL).c_str(),	     \
		NULL);	
	return ret;
}

/*--------------------------------------------------------------------------*/
/**
  	MAIN 
*/
/*--------------------------------------------------------------------------*/
int main(int argc, char * argv[])
{
	char* vm_root;

	if (argc==2) 
	{
		vm_root = getenv("VMCHECKER_ROOT");
		
		if (vm_root == NULL)
		{
			cerr << "[COMMANDER] VMCHECKER_ROOT "
				"variable not initialized"    \
			     << endl;
			exit(-1);
		}
		vmchecker_root_local = strdup(vm_root);
		assert(vmchecker_root_local != NULL);
		parse_ini_files(argv[1], escape(concatenate(                 \
					vmchecker_root_local,   	     \
					"/vm_config.ini", NULL)).c_str());

		if (get_archives() != 0)
			abort_job();

		if (start_executor() != 0) 
        {
            cerr << "[COMMANDER] start_executor() failed" << endl;
            // fall through and upload all build & check logs
        }

		if (upload_results() != 0)
		{
            prepare_for_results_upload();
			unzip_homework();
			abort_job();
		}

		if (unzip_homework() != 0)
			abort_job();

		if (remove_config_file(argv[1]) != 0)
			abort_job();

		free_resources();

		if (clear_jobs_dir() != 0)
			exit (-1);
	}
return 0;

}

