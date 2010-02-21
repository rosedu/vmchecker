package ro.pub.cs.vmchecker.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.user.client.ui.RootPanel;

public class Vmchecker implements EntryPoint {

public void onModuleLoad() {
		HandlerManager eventBus = new HandlerManager(null); 
		AppController appCtrl = new AppController(eventBus); 
		appCtrl.go(RootPanel.get()); 
	}
}
