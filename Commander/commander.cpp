/*
 * commander.cpp - Commands VMExecutor 
 *
 * (C) 2008 Adriana Szekeres <aaa_sz@yahoo.com>
 * 
 */

#include <stdio.h>
#include <fstream>
#include <iostream>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <unistd.h>
#include "log.h"
#include "checker.h"

#include <fcntl.h>
#include <sys/wait.h>


using namespace std;

extern "C" {
#include "iniparser.h"
}


static char* vmchecker_root;			//course root
static char* vm_name;				//virtual machine's name
static char* username;				//tester system's username
static char* ip;				//upload system's ip address
static char* job_id;				//homework's name
static char* user_id;				//student's name
static char* deadline;				//homework's deadline
static char* upload_time;			//homework's upload time
static char* penalty_script;			//path to penalty script 
static char* kernel_msg;			//kernel messages enable
static char* local_ip;				//tester system's ip address
static char* vm_path;				//path to vm's configuration file
static char* guest_user;			//vm's username
static char* guest_pass;			//vm's password	
static char* guest_base_path;			//path to vm's working directory (home directory)
static char* guest_shell_path;			//path to vm's shell
static char* guest_home_in_bash;		//path to working directory in shell (used for cd command in build/run .sh)

static string upload_s;				//upload time directory name
static string jobs_path;			//path to temporary working files for executor
static string scripts_path;			//path to build/run script for vms

static	dictionary* instance; 			//homework.ini
static	dictionary* v_machines; 		//tester_vm.ini



/*
*  parses ini files and extracts necessary information
*/
void  parse_ini_files(char * ini_instance,char* ini_v_machines);

/*
* copies archives from upload system 
*/
void get_archives();

/*
* start vm_executor // tb un if sa vad dc jail sau nu
*/
void start_executor();

/*
* verify and upload results 
*/
void upload_results();

/*
* upload file.zip ; unzip file.zip;remove file.zip
*/
void unzip_homework();

/*
* remove .conf file from local and Upload System
*/
void remove_config_file(char* ini_instance);

/*
* free resources (the 2 dictionaries used for parsing ini files)
*/
void free_resources();

/*
* deletes files/directories from executor_jobs directory
*/
void clear_jobs_dir();

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
 * inspects the returning value of the command invoked by system()
 */

void system_return_value(int ret, char* message)
{
	if (ret==-1)
	{
		error("\"system()\" failed\n");
		exit(-1);
	}
	else
	{	
		if (WIFEXITED(ret)&&(WEXITSTATUS(ret) != 0))
		{
			error("%s\n",message);
			exit(-1);
		}
	}
}

/*
 * extracts .conf file name from .conf file path
 */

char* conf_file(char conf[])
{
	char* a1;
	char* a2;
	
	for(a1=strtok(conf,"/");a1!=NULL;a1=strtok(NULL,"/"))
	{
		a2=a1;
	}
	return a2;
}


/*
 * returns a string that replaces " " by "\ " in str
 */

string replace_spaces(char* str)
{
	string aux;
	
	while(*str!=0)
	{
		if(*str==' ')
			aux+="\\ ";
		else 
			aux+=*str;
		str++;
	}	
	
	return aux;
}

int main(int argc, char * argv[])
{

	if (argc==2) 
	{
		parse_ini_files(argv[1],(char*)"checker.ini");
		get_archives();
		start_executor();
		upload_results();
		unzip_homework();
		remove_config_file(argv[1]);
		free_resources();
		clear_jobs_dir();
	}
	
	return 0;
}


void parse_ini_files(char *ini_instance,char* ini_v_machines)
{
	string temp;
	
	instance = iniparser_load(ini_instance);
	if (instance==NULL) {
		error("Cannot parse file: %s\n", ini_instance);
		exit(-1) ;
	}

	v_machines=iniparser_load(ini_v_machines);
	if (v_machines==NULL){
		error("Cannot parse file: %s\n",ini_v_machines);
		exit(-1);
	}


//	iniparser_dump(instance, stderr);
//	iniparser_dump(v_machines,stderr);

	/* extracting homework info */
	vmchecker_root=iniparser_getstring(instance,"Global:VMCheckerRoot",NULL);
	vm_name=iniparser_getstring(instance,"Global:VMName",NULL);
	job_id=iniparser_getstring(instance,"Global:Job",NULL);
	user_id=iniparser_getstring(instance,"Global:UserId",NULL);
	deadline=iniparser_getstring(instance,"Global:Deadline",NULL);
	upload_time=iniparser_getstring(instance,"Global:UploadTime",NULL);
	penalty_script=iniparser_getstring(instance,"Global:Penalty",NULL);
	kernel_msg=iniparser_getstring(instance,"Global:KernelMsg",NULL);
	ip=iniparser_getstring(instance,"Global:UploadIP",NULL);
	upload_s=replace_spaces(upload_time);

	temp=vm_name;

	/*extracting vm info */ 
	local_ip=iniparser_getstring(v_machines,"Global:LocalAddress",NULL);
	username=iniparser_getstring(v_machines,"Global:TesterUsername",NULL);
	vm_path=iniparser_getstring(v_machines,(temp+":VMPath").c_str(),NULL);
	guest_user=iniparser_getstring(v_machines,(temp+":GuestUser").c_str(),NULL);
	guest_pass=iniparser_getstring(v_machines,(temp+":GuestPassword").c_str(),NULL);
	guest_base_path=iniparser_getstring(v_machines,(temp+":GuestBasePath").c_str(),NULL);
	guest_shell_path=iniparser_getstring(v_machines,(temp+":GuestShellPath").c_str(),NULL);
	guest_home_in_bash=iniparser_getstring(v_machines,(temp+":GuestHomeInBash").c_str(),NULL);
}


void get_archives()
{
	string temp;
	int ret;

	jobs_path=temp+vmchecker_root+"/executor_jobs/";
		

	//get CHECKER_FILE
	ret=system((temp+"scp "+username+"@"+ip+":"+"\"" +vmchecker_root+ "/"+job_id+ "/"+user_id+ "/"+upload_s+ "/"+ CHECKER_FILE+"\" "+ jobs_path+ CHECKER_FILE).c_str());

	system_return_value(ret,(char*)"Cannot get file.zip from Upload System");

	//get CHECKER_TEST
	ret=system((temp+"scp "+username+"@"+ip+":"+vmchecker_root+"/"+"tests"+"/"+job_id+".zip "+jobs_path+"/"+ CHECKER_TEST).c_str());


	system_return_value(ret,(char*)"Cannot get tests.zip from Upload System");
}

void start_executor()
{
	string temp="bash -c \"";
	int ret;	

	/* TODO: apelat cu >> vm_executor.log*/

	ret=system((temp+vmchecker_root+ "/bin/"+"vm_executor "+"\'"+vm_name+"\'"+" "+"\'"+kernel_msg+"\'"+" "+"\'"+vm_path+"\'"+" "+local_ip+" "+"\'"+guest_user+"\'"+" "+"\'"+guest_pass+"\'"+" "+"\'"+guest_base_path+"\'"+" "+"\'"+guest_shell_path+"\'"+" "+"\'"+guest_home_in_bash+"\'"+" "+"\'"+vmchecker_root+"\'"+ "\"").c_str());

	system_return_value(ret,(char*)"VMExecutor failed");
}

void upload_results()
{
	string temp;
	int ret,bugs_c;
	string first_line;


	//upload build
	ret=system((temp+"scp "+jobs_path+"/"+BUILD_OUTPUT_FILE+" "+username+ "@"+ip+":"+"\""+vmchecker_root+ "/"+ "checked"+ "/"+ job_id+ "/"+user_id+ "/"+upload_s+"/"+BUILD_OUTPUT_FILE+"\"" ).c_str());

	system_return_value(ret,(char*)"Cannot upload build_output_file");

	//read first line in RESULT_OUTPUT_FILE "0"/"ok" 
	fstream results_file;

	results_file.open((temp+jobs_path+RESULT_OUTPUT_FILE).c_str(),ios::in);

	if (!results_file.is_open())
	{
		error("unable to open file %s\n", RESULT_OUTPUT_FILE);
		exit(-1);
	}

	getline(results_file,first_line);
	results_file.close();

	
	if (first_line=="0") //homework doesn't compile
	{
		append_f((temp+jobs_path+BUILD_OUTPUT_FILE).c_str(), (temp+jobs_path+RESULT_OUTPUT_FILE).c_str(), "\n     ===== BUILD RESULTS =====\n");

	}
	else
	{

		//check deadline 
		/*t=system((temp+"/"+penalty_script+" >> "+jobs_path+RESULT_OUTPUT_FILE).c_str());

		system_return_value(ret,(char*)"Cannot check deadline");
		*/

		append_f((temp+jobs_path+BUILD_OUTPUT_FILE).c_str(), (temp+jobs_path+RESULT_OUTPUT_FILE).c_str(), "\n     ===== BUILD RESULTS =====\n");

		if (atoi(kernel_msg))
		{
			bugs_c = check_bugs();
			if (bugs_c == -1)
			{
				error("System error: check_bugs failed\n");
				exit(-1);
			}

			results_file.open((temp+jobs_path+RESULT_OUTPUT_FILE).c_str(),ios::trunc);
	
			if (bugs_c > 0)
			{
				results_file << "0\n" << endl;
				results_file << "-10: au fost identificate " << bugs_c << " bug-uri" << endl;
				
				exit(0);
			}
	
			results_file.close();
			
			append_f((temp+jobs_path+KMESSAGE_OUTPUT_FILE).c_str(), (temp+jobs_path+RESULT_OUTPUT_FILE).c_str(), "\n     ===== KERNEL MESSAGES =====\n");
	
			//upload KMESSAGE_OUTPUT_FILE
			ret=system((temp+"scp "+jobs_path+"/"+KMESSAGE_OUTPUT_FILE+" "+username+ "@"+ip+ ":"+"\""+ vmchecker_root+"/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_s+ "/"+ RUN_OUTPUT_FILE +" \"").c_str());

			system_return_value(ret,(char*)"Cannot upload kmessage_output_file");
		}


		append_f((temp+jobs_path+RUN_OUTPUT_FILE).c_str(), (temp+jobs_path+ RESULT_OUTPUT_FILE).c_str() , "\n     ===== RUN RESULTS =====\n");

		//upload  RUN_OUTPUT_FILE
		ret=system((temp+"scp "+jobs_path+"/"+RUN_OUTPUT_FILE+ " "+ username+"@"+ ip+":"+"\""+ vmchecker_root+ "/"+ "checked"+"/"+ job_id+ "/"+user_id+"/" +upload_s+ "/"+  RUN_OUTPUT_FILE+"\"").c_str());
	
		system_return_value(ret,(char*)"Cannot upload run_output_file");
	}

	
	//upload RESULT_OUTPUT_FILE
	ret=system((temp+"scp "+jobs_path+"/"+RESULT_OUTPUT_FILE+ " "+ username+"@"+ ip+":"+"\""+vmchecker_root+ "/"+ "checked"+"/"+ job_id+ "/"+user_id+"/"+upload_s+"/"+RESULT_OUTPUT_FILE+"\"").c_str());

	system_return_value(ret,(char*)"Cannot upload result_output_file");
}

void unzip_homework()
{
	string temp;
	int ret;

	ret=system((temp+"scp "+jobs_path+"/"+ CHECKER_FILE+ username+ "@"+ ip+":"+ "\""+ vmchecker_root+ "/"+ "checked"+ "/"+ job_id+"/"+user_id+"/"+upload_s+"/"+CHECKER_FILE+"\"" ).c_str());

	system_return_value(ret,(char*)"Cannot upload file.zip");

	ret=system((temp+"ssh "+username+"@"+ip+" "+"\"unzip "+vmchecker_root+ "/"+"checked"+ "/"+job_id+"/"+user_id+ "/"+upload_s+"/"+CHECKER_FILE+" -d "+vmchecker_root+ "/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_s+"/\"" ).c_str());

	system_return_value(ret,(char*)"Cannot unzip file.zip on Upload System");

	ret=system((temp+"ssh "+username+"@"+ip+" "+"\"rm -f "+ vmchecker_root+ "/"+ "checked"+ "/"+job_id+ "/"+ user_id+"/"+upload_s+"/"+CHECKER_FILE+"\"" ).c_str());

	system_return_value(ret,(char*)"Cannot remove file.zip from Upload System");
}

void remove_config_file(char* ini_instance)
{
	string temp;
	int ret;

	ret=system((temp+"rm -f "+ini_instance).c_str());

	system_return_value(ret,(char*)"Cannot remove .conf file from Tester System");

	ret=system((temp+"ssh "+username+"@"+ip+" "+"\"rm -f "+ vmchecker_root+ "/"+ "unchecked"+ "/"+ (char*)conf_file(ini_instance)+ "\"").c_str());

	system_return_value(ret,(char*)"Cannot remove .conf file from Upload System");
}

void free_resources()
{
	iniparser_freedict(instance);
	iniparser_freedict(v_machines);
}

void clear_jobs_dir()
{
	string temp;
	int ret;

	ret=system((temp+"rm -rf " +jobs_path+"/*" ).c_str());

	system_return_value(ret,(char*)"Cannot clear executor_jobs directory");
}
