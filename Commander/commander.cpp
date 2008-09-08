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


int  parse_ini_files(char * ini_instance,char* ini_v_machines);

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
 * inspectes the returning value of the command invoked by system()
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
 * return a string that replaces " " by "\ " in str
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
	int status ;

	if (argc==2) {
		status = parse_ini_files(argv[1],(char*)"checker.ini");
	}
	
	return status ;
}

int parse_ini_files(char *ini_instance,char* ini_v_machines)
{
	string temp;
	int ret,bugs_c;
	string first_line;

	dictionary* instance; 	//homework.ini
	dictionary* v_machines; //tester_vm.ini

	char* base_path;
	char* vm_name;
	char* username;
	char* ip;
	char* job_id;
	char* user_id;
	char* deadline;
	char* upload_time;
	char* penalty;
	char* kernel_msg;
	char* local_ip;
	char* vm_path;
	char* guest_user;
	char* guest_pass;
	char* guest_base_path;
	char* guest_shell_path;
	char* guest_home_in_bash;
	
	string upload_s;

	instance = iniparser_load(ini_instance);
	if (instance==NULL) {
		error("Cannot parse file: %s\n", ini_instance);
		return -1 ;
	}

	v_machines=iniparser_load(ini_v_machines);
	if (v_machines==NULL){
		error("Cannot parse file: %s\n",ini_v_machines);
		return -1;
	}


//	iniparser_dump(instance, stderr);
//	iniparser_dump(v_machines,stderr);

	/* extracting homework info */
	base_path=iniparser_getstring(instance,"Global:BasePath",NULL);
	vm_name=iniparser_getstring(instance,"Global:VMName",NULL);
	job_id=iniparser_getstring(instance,"Global:Job",NULL);
	user_id=iniparser_getstring(instance,"Global:UserId",NULL);
	deadline=iniparser_getstring(instance,"Global:Deadline",NULL);
	upload_time=iniparser_getstring(instance,"Global:UploadTime",NULL);
	penalty=iniparser_getstring(instance,"Global:Penalty",NULL);
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

	temp="";

	
/*
* get archives from Upload System
*/
	//printf("Get archives\n");

	//printf("Cmd1=%s\n",(temp+"scp "+username+"@"+ip+":"+base_path+"/"+job_id+"/"+user_id+"/"+upload_s+"/"+"file.zip "+jobs_path+"/"+"file.zip").c_str());

	ret=system((temp+"scp "+username+"@"+ip+":"+"\""+base_path+"/"+job_id+"/"+user_id+"/"+upload_s+"/"+"file.zip\" "+jobs_path+"/"+"file.zip").c_str());

	system_return_value(ret,(char*)"Cannot get file.zip from Upload System");

	//printf("Cmd2=%s\n",(temp+"scp "+username+"@"+ip+":"+base_path+"/"+"tests"+"/"+job_id+".zip "+jobs_path+"/"+"tests.zip").c_str());

	ret=system((temp+"scp "+username+"@"+ip+":"+base_path+"/"+"tests"+"/"+job_id+".zip "+jobs_path+"/"+"tests.zip").c_str());


	system_return_value(ret,(char*)"Cannot get tests.zip from Upload System");

	/*
	* start vm_executor // tb un if sa vad dc jail sau nu
	*/
	temp="bash -c \"";
	
	//printf("Cmd3=%s\n",(temp+"./vm_executor "+vm_name+" "+vm_path+" "+local_ip+" "+guest_user+" "+guest_pass+" "+guest_base_path+" "+guest_shell_path+" "+guest_home_in_bash+"\"").c_str());

	/* TODO: calea spe vm_executor si apelat cu >> vm_executor.log*/
	ret=system((temp+"./vm_executor "+vm_name+" "+kernel_msg+" "+vm_path+" "+local_ip+" "+guest_user+" "+guest_pass+" "+guest_base_path+" "+guest_shell_path+" "+guest_home_in_bash+"\"").c_str());

	system_return_value(ret,(char*)"VMExecutor failed");

/*
* verify and upload results 
*/
	temp="";

	/*
	* upload build
	*/

	//printf("Cmd4=%s\n",(temp+"scp "+jobs_path+"/"+BUILD_OUTPUT_FILE+" "+username+ "@"+ip+":"+base_path+ "/"+ "checked"+ "/"+ job_id+ "/"+user_id+ "/"+upload_time+"/"+"job_build" ).c_str());



	ret=system((temp+"scp "+jobs_path+"/"+BUILD_OUTPUT_FILE+" "+username+ "@"+ip+":"+"\""+base_path+ "/"+ "checked"+ "/"+ job_id+ "/"+user_id+ "/"+upload_s+"/"+"job_build \"" ).c_str());

	system_return_value(ret,(char*)"Cannot upload build_output_file");

	/* read first line in RESULT_OUTPUT_FILE "0"/"ok" */
	fstream results_file;

	results_file.open((temp+jobs_path+RESULT_OUTPUT_FILE).c_str(),ios::in);

	if (!results_file.is_open())
	{
		error("unable to open file %s\n", RESULT_OUTPUT_FILE);
		return -1;
	}

	getline(results_file,first_line);
	results_file.close();

	
	if (first_line=="0") //homework doesn't compile
	{
		append_f((temp+jobs_path+BUILD_OUTPUT_FILE).c_str(), (temp+jobs_path+RESULT_OUTPUT_FILE).c_str(), "\n     ===== BUILD RESULTS =====\n");

	}
	else
	{

		/*
		* check deadline 
		*/

		//TODO: de modificat calea scriptului pt. deadline si jobs_path care este momentan in header
		/*t=system((temp+"./deadline.py >> "+jobs_path+RESULT_OUTPUT_FILE).c_str());

		system_return_value(ret,(char*)"Cannot check deadline");
		*/
		append_f((temp+jobs_path+BUILD_OUTPUT_FILE).c_str(), (temp+jobs_path+RESULT_OUTPUT_FILE).c_str(), "\n     ===== BUILD RESULTS =====\n");

		if (atoi(kernel_msg))
		{
			bugs_c = check_bugs();
			if (bugs_c == -1)
			{
				error("System error: check_bugs failed\n");
				return -1;
			}

			results_file.open((temp+jobs_path+RESULT_OUTPUT_FILE).c_str(),ios::trunc);
	
			if (bugs_c > 0)
			{
				results_file << "0\n" << endl;
				results_file << "-10: au fost identificate " << bugs_c << " bug-uri" << endl;
				
				return 0;
			}
	
			results_file.close();
			
			append_f((temp+jobs_path+KMESSAGE_OUTPUT_FILE).c_str(), (temp+jobs_path+RESULT_OUTPUT_FILE).c_str(), "\n     ===== KERNEL MESSAGES =====\n");
	
			/*
			* upload KMESSAGE_OUTPUT_FILE
			*/
			ret=system((temp+"scp "+jobs_path+"/"+KMESSAGE_OUTPUT_FILE+" "+username+ "@"+ip+ ":"+"\""+base_path+"/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_s+ "/"+ "job_run \"").c_str());

			system_return_value(ret,(char*)"Cannot upload kmessage_output_file");
		}


		append_f((temp+jobs_path+RUN_OUTPUT_FILE).c_str(), (temp+jobs_path+ RESULT_OUTPUT_FILE).c_str() , "\n     ===== RUN RESULTS =====\n");

		/*
		*  upload  RUN_OUTPUT_FILE
		*/
		ret=system((temp+"scp "+jobs_path+"/"+RUN_OUTPUT_FILE+ " "+ username+"@"+ ip+":"+"\""+ base_path+ "/"+ "checked"+"/"+ job_id+ "/"+user_id+"/" +upload_s+ "/"+ "job_run\"").c_str());
	
		system_return_value(ret,(char*)"Cannot upload run_output_file");
	}

	
	/*
	* upload RESULT_OUTPUT_FILE
	*/

	ret=system((temp+"scp "+jobs_path+"/"+RESULT_OUTPUT_FILE+ " "+ username+"@"+ ip+":"+"\""+base_path+ "/"+ "checked"+"/"+ job_id+ "/"+user_id+"/"+upload_s+"/"+"job_results\"").c_str());

	system_return_value(ret,(char*)"Cannot upload result_output_file");

	/*
	* upload file.zip ; unzip file.zip;remove file.zip
	*/
	ret=system((temp+"scp "+jobs_path+"/"+"file.zip "+username+"@"+ip+":"+"\""+base_path+"/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_s+"/"+"file.zip\"" ).c_str());

	system_return_value(ret,(char*)"Cannot upload file.zip");

	ret=system((temp+"ssh "+username+"@"+ip+" "+"\"unzip "+base_path+ "/"+"checked"+ "/"+job_id+"/"+user_id+ "/"+upload_s+"/"+"file.zip "+" -d "+base_path+"/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_s+"/\"" ).c_str());

	system_return_value(ret,(char*)"Cannot unzip file.zip on Upload System");

	ret=system((temp+"ssh "+username+"@"+ip+" "+"\"rm -f "+base_path+"/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_s+"/"+"file.zip\"" ).c_str());

	system_return_value(ret,(char*)"Cannot remove file.zip from Upload System");

	/*
	* remove .conf file from local and Upload System
	*/


	ret=system((temp+"rm -f "+ini_instance).c_str());

	system_return_value(ret,(char*)"Cannot remove .conf file from Tester System");

	ret=system((temp+"ssh "+username+"@"+ip+" "+"\"rm -f "+base_path+"/"+"unchecked"+"/"+(char*)conf_file(ini_instance)+"\"").c_str());

	system_return_value(ret,(char*)"Cannot remove .conf file from Upload System");

	/*
	* free resources
	*/
	iniparser_freedict(instance);
	iniparser_freedict(v_machines);

	return 0 ;
}

