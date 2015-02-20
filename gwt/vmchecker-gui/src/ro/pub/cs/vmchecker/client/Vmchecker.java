package ro.pub.cs.vmchecker.client;

import ro.pub.cs.vmchecker.client.service.HTTPService;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.event.shared.SimpleEventBus;
import com.google.gwt.user.client.ui.RootPanel;

public class Vmchecker implements EntryPoint {

	public void onModuleLoad() {
		SimpleEventBus eventBus = new SimpleEventBus();
		try {
			HTTPService rpcService = new HTTPService(eventBus);
			AppController appCtrl = new AppController(eventBus, rpcService);
			appCtrl.go(RootPanel.get());
		} catch (Exception e) {
			ExceptionHandler.getInstance().setEventBus(eventBus);
			ExceptionHandler.getInstance().exceptionError(e);
		}
	}
}
