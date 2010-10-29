package ro.pub.cs.vmchecker.client.service;

import ro.pub.cs.vmchecker.client.i18n.VmcheckerConstants;
import ro.pub.cs.vmchecker.client.event.AuthenticationEvent;
import ro.pub.cs.vmchecker.client.event.ErrorDisplayEvent;
import ro.pub.cs.vmchecker.client.model.ErrorResponse;
import ro.pub.cs.vmchecker.client.service.json.ErrorResponseDecoder;
import ro.pub.cs.vmchecker.client.service.json.JSONDecoder;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.HandlerManager;

public class ServiceError {

	private HandlerManager eventBus;
	private static VmcheckerConstants constants = GWT
			.create(VmcheckerConstants.class);
	private String URL;

	public ServiceError(HandlerManager eventBus, String URL) {
		this.eventBus = eventBus;
		this.constants = constants;
		this.URL = URL;
	}

	public void parseError(String text) {
		try {
			ErrorResponseDecoder decoder = new ErrorResponseDecoder();
			ErrorResponse serviceError = decoder.decode(text);
			if (serviceError.isAuthError()) {
				eventBus.fireEvent(new AuthenticationEvent(AuthenticationEvent.EventType.ERROR));
			} else {
				eventBus.fireEvent(new ErrorDisplayEvent(constants.serviceError() + " " + serviceError.message, serviceError.trace));
			}
		} catch (Exception e) {
			GWT.log("[parseError()]", e);
			/* unexpected format */
			eventBus.fireEvent(new ErrorDisplayEvent(constants.serviceError() + " " + constants.unknownFormat(),
					"<b>Service URL</b>: " + URL + "<br/><b>Content</b>:<br/>" + text));
		}
	}

}
