#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <unistd.h>

using namespace std;

extern "C" {
#include "iniparser.h"
}

char* base_path;
char* tester;
char* vm_name;


int  parse_ini_files(char * ini_instance,char* ini_v_machines,char* conf);
int get_archives(char* source,char* destination,char* username,char* ip);

int main(int argc, char * argv[])
{
	int status ;

	if (argc==2) {
		status = parse_ini_files(argv[1],(char*)"checker.ini",argv[1]);
	}
	return status ;
}

int parse_ini_files(char *ini_instance,char* ini_v_machines,char* conf)
{
	string temp;

	dictionary* instance; //instanta tema
	dictionary* v_machines; //fisier de configurare vms

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
		fprintf(stderr, "cannot parse file: %s\n", ini_instance);
		return -1 ;
	}

	v_machines=iniparser_load(ini_v_machines);
	if (v_machines==NULL){
		fprintf(stderr,"cannot parse file: %s\n",ini_v_machines);
		return -1;
	}


//	iniparser_dump(instance, stderr);
//	iniparser_dump(v_machines,stderr);

	//extrag din instanta de tema
	base_path=iniparser_getstring(instance,"Global:BasePath",NULL);
	vm_name=iniparser_getstring(instance,"Global:VMName",NULL);
	job_id=iniparser_getstring(instance,"Global:Job",NULL);
	user_id=iniparser_getstring(instance,"Global:UserId",NULL);
	deadline=iniparser_getstring(instance,"Global:Deadline",NULL);
	upload_time=iniparser_getstring(instance,"Global:UploadTime",NULL);
	penalty=iniparser_getstring(instance,"Global:Penalty",NULL);
	kernel_msg=iniparser_getstring(instance,"Global:KernelMsg",NULL);
	//jobs_path=iniparser_getstring(v_machines,"Global:JobsPath",NULL);
	//username=iniparser_getstring(v_machines,"Global:TesterUsername",NULL);
	ip=iniparser_getstring(instance,"Global:UploadIP",NULL);


	temp=vm_name;

	//extrag din fisierul de masini virtuale 
	local_ip=iniparser_getstring(v_machines,"Global:LocalAddress",NULL);
	jobs_path=iniparser_getstring(v_machines,"Global:JobsPath",NULL);
	username=iniparser_getstring(v_machines,"Global:TesterUsername",NULL);
	vm_path=iniparser_getstring(v_machines,(temp+":VMPath").c_str(),NULL);
	guest_user=iniparser_getstring(v_machines,(temp+":GuestUser").c_str(),NULL);
	guest_pass=iniparser_getstring(v_machines,(temp+":GuestPassword").c_str(),NULL);
	guest_base_path=iniparser_getstring(v_machines,(temp+":GuestBasePath").c_str(),NULL);
	guest_shell_path=iniparser_getstring(v_machines,(temp+":GuestShellPath").c_str(),NULL);
//	guest_home_in_bash=iniparser_getstring(v_machines,(temp+"GuestHomeInBash").c_str());


	//get archives
	system((temp+"scp "+username+"@"+ip+":"+base_path+"/"+job_id+"/"+user_id+"/"+upload_time+"file.zip "+jobs_path+"/"+"file.zip").c_str());
	system((temp+"scp "+username+"@"+ip+":"+base_path+"/"+"tests"+"/"+job_id+".zip "+jobs_path+"/"+"tests.zip").c_str());

	//apelez executorul
	
	temp="bash -c \"";
	system((temp+"./executor "+vm_name+" "+ vm_path+" "+local_ip+" "+guest_user+" "+guest_pass+" "+guest_base_path+" "+guest_shell_path+"\"").c_str());

	//verific deadline + warninguri
	//din jobs_path am job_build si job_run
	
	//pun pe sistemul de upload rezultatele
	
	temp="";
	system((temp+"scp "+jobs_path+"/"+"job_build "+username+"@"+ip+":"+base_path+"/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_time+"/"+"job_build" ).c_str());
	system((temp+"scp "+jobs_path+"/"+"job_run "+username+"@"+ip+":"+base_path+"/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_time+"/"+"job_run").c_str());

	//pun arhiva si o dezarhivez
	system((temp+"scp "+jobs_path+"/"+"file.zip "+username+"@"+ip+":"+base_path+"/"+"checked"+"/"+job_id+"/"+user_id+"/"+upload_time+"/"+"file.zip" ).c_str());
	system((temp+"ssh "+username+"@"+ip+" "+"\"unzip "+base_path+"uncheked"+"/"+"file.zip"+"\"").c_str());
	system((temp+"ssh "+username+"@"+ip+" "+"\"rm -f "+base_path+"uncheked"+"/"+"file.zip"+"\"").c_str());

	//sterg fisierul de configurare
	system((temp+"ssh "+username+"@"+ip+" "+"\"rm -f "+base_path+"uncheked"+"/"+conf+"\"").c_str());

	iniparser_freedict(instance);
	iniparser_freedict(v_machines);
	return 0 ;
}

/*int get_archives(char* base_path,char* upload_time,char* user_id,char* job_id char* destination,char* username,char* ip)
{
	string temp;
	
	system((temp+"scp "+base_path+"/"+"file.zip"+" "+username+"@"+ip+":"+destination+"file.zip").c_str());
	system((temp+"scp "+source+"tests.zip"+" "+username+"@"+ip+":"+destination+"tests.zip").c_str());
}*/

