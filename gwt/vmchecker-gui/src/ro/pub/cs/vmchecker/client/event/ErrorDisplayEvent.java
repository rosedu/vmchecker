package ro.pub.cs.vmchecker.client.event;

public class ErrorDisplayEvent extends StatusChangedEvent {

	private String details; 
	
	public ErrorDisplayEvent(String message, String details) {
		super(StatusChangedEvent.StatusType.ERROR, message);
		this.details = details; 
	}

	public String getDetails() {
		return details; 
	}
	
}
