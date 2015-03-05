package ro.pub.cs.vmchecker.client.event;

import java.util.Date;
import com.google.gwt.event.shared.GwtEvent;

public class ServerTimeUpdateEvent extends GwtEvent<ServerTimeUpdateEventHandler> {
	public static final GwtEvent.Type<ServerTimeUpdateEventHandler> TYPE = new GwtEvent.Type<ServerTimeUpdateEventHandler>();

	private Date date;
	public ServerTimeUpdateEvent(Date date) {
		this.date = date;
	}

	public Date getDate() {
		return this.date;
	}
	
	@Override
	protected void dispatch(ServerTimeUpdateEventHandler handler) {
		handler.onServerTimeUpdate(this);
	}

	@Override
	public com.google.gwt.event.shared.GwtEvent.Type<ServerTimeUpdateEventHandler> getAssociatedType() {
		return TYPE; 
	} 
}
