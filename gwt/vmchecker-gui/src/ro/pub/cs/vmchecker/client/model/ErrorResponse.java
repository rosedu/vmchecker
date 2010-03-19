package ro.pub.cs.vmchecker.client.model;

public class ErrorResponse extends Throwable {
	
	private static final long serialVersionUID = 1L;

	public enum Type {
		ERR_AUTH, ERR_EXCEPTION, ERR_OTHER 
	}
	
	public Type type; 
	public String message;
	public String trace; 
	
	public ErrorResponse(int errorCode, String message, String trace) {
		errorCode -= 1; 
		if (errorCode < Type.values().length) {
			this.type = Type.values()[errorCode]; 
		} else {
			this.type = Type.ERR_OTHER; 
		}
		this.message = message; 
		this.trace = trace; 
	}
	
	public boolean isAuthError() {
		return type == Type.ERR_AUTH; 
	}
}
