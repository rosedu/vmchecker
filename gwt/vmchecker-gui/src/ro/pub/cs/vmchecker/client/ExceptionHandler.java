package ro.pub.cs.vmchecker.client;

import ro.pub.cs.vmchecker.client.event.ErrorDisplayEvent;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.EventBus;
import ro.pub.cs.vmchecker.client.i18n.VmcheckerConstants;

public class ExceptionHandler {

	private static ExceptionHandler exceptionHandlerSingleton;

	private EventBus eventBus;
	private static VmcheckerConstants constants = GWT
			.create(VmcheckerConstants.class);

	private ExceptionHandler() { }

	public static ExceptionHandler getInstance() {
		if (exceptionHandlerSingleton == null) {
			exceptionHandlerSingleton = new ExceptionHandler();
		}
		return exceptionHandlerSingleton;
	}

	public void setEventBus(EventBus eventBus) {
		this.eventBus = eventBus;
	}

	public void exceptionError(Exception e) {
		GWT.log("[exceptionError()]", e);
		/* unhandled exception. get stack trace. */

		if (eventBus == null) return;

		StringBuilder sb = new StringBuilder();
		for (StackTraceElement element : e.getStackTrace()) {
			sb.append(element + "<br/>");
		}

		eventBus.fireEvent(new ErrorDisplayEvent(constants.exceptionError() + " " + constants.exceptionErrorText(),
				"<b>" + constants.exceptionErrorContent() + "</b>:<br/>" + e.toString() +
				"<br/>" + sb.toString() + "<br/>"));
	}
}
