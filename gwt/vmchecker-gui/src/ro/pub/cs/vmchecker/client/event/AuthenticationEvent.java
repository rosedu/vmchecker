package ro.pub.cs.vmchecker.client.event;

import com.google.gwt.event.shared.GwtEvent;

import ro.pub.cs.vmchecker.client.model.User;

public class AuthenticationEvent extends GwtEvent<AuthenticationEventHandler> {

	public static final GwtEvent.Type<AuthenticationEventHandler> TYPE
		= new GwtEvent.Type<AuthenticationEventHandler>(); 
	
	public enum EventType {
		SUCCESS, ERROR
	}
	
	private User user;
	private EventType type; 
	
	public AuthenticationEvent(EventType type) {
		this.type = type; 
	}
	
	public AuthenticationEvent(User user) {
		this.type = EventType.SUCCESS; 
		this.user = user;
	}
	
	public EventType getType() {
		return type; 
	}
	
	public User getUser() {
		return user;
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
