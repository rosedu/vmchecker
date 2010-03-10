package ro.pub.cs.vmchecker.client.event;

import com.google.gwt.event.shared.EventHandler;

public interface AuthenticationEventHandler extends EventHandler {
	void onAuthenticationChange(AuthenticationEvent event);  
}
