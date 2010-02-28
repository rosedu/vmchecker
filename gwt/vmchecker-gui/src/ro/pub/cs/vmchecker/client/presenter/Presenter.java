package ro.pub.cs.vmchecker.client.presenter;

import com.google.gwt.user.client.ui.HasWidgets;

public interface Presenter {
	
	public void go(final HasWidgets container); 
	public void clearEventHandlers(); 
}
