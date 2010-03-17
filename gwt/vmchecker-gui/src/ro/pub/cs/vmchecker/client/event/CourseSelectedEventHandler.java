package ro.pub.cs.vmchecker.client.event;

import com.google.gwt.event.shared.EventHandler;

public interface CourseSelectedEventHandler extends EventHandler {
	void onSelect(CourseSelectedEvent event); 
}
