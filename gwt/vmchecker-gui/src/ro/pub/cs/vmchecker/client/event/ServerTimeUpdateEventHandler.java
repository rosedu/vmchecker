package ro.pub.cs.vmchecker.client.event;

import com.google.gwt.event.shared.EventHandler;

public interface ServerTimeUpdateEventHandler extends EventHandler {
	void onServerTimeUpdate(ServerTimeUpdateEvent event); 
}
