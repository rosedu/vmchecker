package ro.pub.cs.vmchecker.client.event;

import com.google.gwt.event.shared.GwtEvent;

public class AuthenticationEvent extends GwtEvent<AuthenticationEventHandler> {

	public static final GwtEvent.Type<AuthenticationEventHandler> TYPE
		= new GwtEvent.Type<AuthenticationEventHandler>(); 
	
	public enum EventType {
		SUCCESS, ERROR
	}
	
	private String username; 
	private EventType type; 
	
	public AuthenticationEvent(EventType type) {
		this.type = type; 
	}
	
	public AuthenticationEvent(String username) {
		this.type = EventType.SUCCESS; 
		this.username = username; 
	}
	
	public EventType getType() {
		return type; 
	}
	
	public String getUsername() {
		return username; 
	}
	
	@Override
	protected void dispatch(AuthenticationEventHandler handler) {
		handler.onAuthenticationChange(this); 
	}

	@Override
	public com.google.gwt.event.shared.GwtEvent.Type<AuthenticationEventHandler> getAssociatedType() {
		return TYPE; 
	}

}
