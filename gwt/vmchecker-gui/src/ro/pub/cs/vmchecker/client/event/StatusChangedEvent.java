package ro.pub.cs.vmchecker.client.event;

import com.google.gwt.event.shared.GwtEvent;

public class StatusChangedEvent extends GwtEvent<StatusChangedEventHandler> {
	public static final GwtEvent.Type<StatusChangedEventHandler> TYPE = new GwtEvent.Type<StatusChangedEventHandler>();

	public enum StatusType {
		INFO, SUCCESS, ACTION, ERROR, RESET
	}
	
	private StatusType type; 
	private String text;
	
	public StatusChangedEvent(StatusType type, String text) {
		this.type = type; 
		this.text = text; 
	}
	
	
	
	public String getText() {
		return text; 
	}
	
	public StatusType getType() {
		return type; 
	}
	
	@Override
	protected void dispatch(StatusChangedEventHandler handler) {
		handler.onChange(this); 
	}

	@Override
	public com.google.gwt.event.shared.GwtEvent.Type<StatusChangedEventHandler> getAssociatedType() {
		return TYPE; 
	} 
}
