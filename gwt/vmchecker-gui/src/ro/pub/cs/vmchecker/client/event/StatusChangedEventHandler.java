package ro.pub.cs.vmchecker.client.event;

import com.google.gwt.event.shared.EventHandler;

public interface StatusChangedEventHandler extends EventHandler {
	void onChange(StatusChangedEvent event); 
}
