package ro.pub.cs.vmchecker.client;

import ro.pub.cs.vmchecker.client.service.HTTPService;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.user.client.ui.RootPanel;

public class Vmchecker implements EntryPoint {

public void onModuleLoad() {
		HandlerManager eventBus = new HandlerManager(null);
		HTTPService rpcService = new HTTPService(eventBus);
		AppController appCtrl = new AppController(eventBus, rpcService); 
		appCtrl.go(RootPanel.get()); 
	}
}
