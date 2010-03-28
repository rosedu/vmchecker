package ro.pub.cs.vmchecker.client.model;

public class Assignment {
	public String id; 
	public String title; 
	public String deadline;
	public String statementLink; 
	
	public Assignment(String id, String title, String deadline, String statementLink) {
		this.id = id; 
		this.title = title;
		this.deadline = deadline;
		this.statementLink = statementLink; 
	}

}
