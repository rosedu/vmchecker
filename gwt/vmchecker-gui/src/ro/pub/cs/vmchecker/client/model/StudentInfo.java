package ro.pub.cs.vmchecker.client.model;

import java.util.HashMap;

public class StudentInfo {

	public String name; 
	public String id; 
	public HashMap<String, String> results; 
	
	public StudentInfo(String name, String id, HashMap<String, String> results) {
		this.name = name; 
		this.id = id; 
		this.results = results; 
	}
}
