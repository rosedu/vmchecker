#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <unistd.h>
#include "log.h"
#include <sys/wait.h>


using namespace std;

extern "C" {
#include "iniparser.h"
}


int  parse_ini_files(char * ini_instance,char* ini_v_machines);

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
		printf("%s\n",a1);
		a2=a1;
	}
	return a2;
}


int main(int argc, char * argv[])
{
	int status ;

	if (argc==2) {
		status = parse_ini_files(argv[1],(char*)"checker.ini");
	}
	
	printf("fis=%s\n",conf_file(argv[1]));
	

	return status ;
}

int parse_ini_files(char *ini_instance,char* ini_v_machines)
{
	string temp;
	int ret;

	dictionary* instance; 	//homework.ini
	dictionary* v_machines; //tester_vm.ini

	char* base_path;
	char* vm_name;
	char* jobs_path;
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


	temp=vm_name;

	/*extracting vm info */ 
	local_ip=iniparser_getstring(v_machines,"Global:LocalAddress",NULL);
	jobs_path=iniparser_getstring(v_machines,"Global:JobsPath",NULL);
	username=iniparser_getstring(v_machines,"Global:TesterUsername",NULL);
	vm_path=iniparser_getstring(v_machines,(temp+":VMPath").c_str(),NULL);
	guest_user=iniparser_getstring(v_machines,(temp+":GuestUser").c_str(),NULL);
	guest_pass=iniparser_getstring(v_machines,(temp+":GuestPassword").c_str(),NULL);
	guest_base_path=iniparser_getstring(v_machines,(temp+":GuestBasePath").c_str(),NULL);
	guest_shell_path=iniparser_getstring(v_machines,(temp+":GuestShellPath").c_str(),NULL);
	guest_home_in_bash=iniparser_getstring(v_machines,(temp+"GuestHomeInBash").c_str(),NULL);

	temp="";

	/* get archives from Upload System*/
	ret=system((temp+"scp "+username+"@"+ip+":"+base_path+"/"+job_id+"/"+user_id+"/"+upload_time+"file.zip "+jobs_path+"/"+"file.zip").c_str());

	system_return_value(ret,"Cannot get file.zip from Upload System");

	ret=system((temp+"scp "+username+"@"+ip+":"+base_path+"/"+"tests"+"/"+job_id+".zip "+jobs_path+"/"+"tests.zip").c_str());

	system_return_value(ret,"Cannot get tests.zip from Upload System");

	/* start vm_executor // tb un if sa vad dc jail sau nu*/
	temp="bash -c \"";

	ret=system((temp+"./vm_executor "+vm_name+" "+ vm_path+" "+local_ip+" "+guest_user+" "+guest_pass+" "+guest_base_path+" "+guest_shell_path+"\"").c_str());

	system_return_value(ret,"VMExecutor failed");

	/* upload results */
	temp="";

	ret=system((temp+"scp "+jobs_path+"/"+"job_build "+username+"@"+ip+":"+base_path+"/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_time+"/"+"job_build" ).c_str());

	system_return_value(ret,"Cannot upload job_build");

	ret=system((temp+"scp "+jobs_path+"/"+"job_run "+username+"@"+ip+":"+base_path+"/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_time+"/"+"job_run").c_str());

	system_return_value(ret,"Cannot upload job_run");

	/*upload file.zip ; unzip file.zip;remove file.zip*/
	ret=system((temp+"scp "+jobs_path+"/"+"file.zip "+username+"@"+ip+":"+base_path+"/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_time+"/"+"file.zip" ).c_str());

	system_return_value(ret,"Cannot upload file.zip");

	ret=system((temp+"ssh "+username+"@"+ip+" "+"\"unzip "+base_path+"uncheked"+"/"+"file.zip"+"\"").c_str());

	system_return_value(ret,"Cannot unzip file.zip on Upload System");

	ret=system((temp+"ssh "+username+"@"+ip+" "+"\"rm -f "+base_path+"uncheked"+"/"+"file.zip"+"\"").c_str());

	system_return_value(ret,"Cannot remove file.zip from Upload System");

	/* remove .conf file */
	ret=system((temp+"ssh "+username+"@"+ip+" "+"\"rm -f "+base_path+"uncheked"+"/"+(char*)conf_file(ini_instance)+"\"").c_str());

	system_return_value(ret,"Cannot remove .conf file from Upload System");

	/* free resources */
	iniparser_freedict(instance);
	iniparser_freedict(v_machines);

	return 0 ;
}

