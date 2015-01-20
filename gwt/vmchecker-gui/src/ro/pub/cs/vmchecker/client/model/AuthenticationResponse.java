package ro.pub.cs.vmchecker.client.model;

public class AuthenticationResponse {
	
	public boolean status; 
	public User user;
	public String info; 
	
	public AuthenticationResponse(boolean status, User user, String info) {
		this.status = status; 
		this.user = user;
		this.info = info; 
	}
}
