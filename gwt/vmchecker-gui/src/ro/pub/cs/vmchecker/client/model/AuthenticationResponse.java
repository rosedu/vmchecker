package ro.pub.cs.vmchecker.client.model;

public class AuthenticationResponse {
	
	public boolean status; 
	public String username; 
	public String info; 
	
	public AuthenticationResponse(boolean status, String username, String info) {
		this.status = status; 
		this.username = username; 
		this.info = info; 
	}
}
