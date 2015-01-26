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
		this.URL = URL;
	}

	public void serverError(int statusCode, String statusMessage, String text) {
		eventBus.fireEvent(new ErrorDisplayEvent(constants.serviceError() + " " + constants.badServerStatusCode(),
				"<b>" + constants.serviceErrorUrl() + "</b>: " + URL + "<br/>" +
				"<b>" + constants.serviceErrorStatusCode() + "</b>: " + statusCode + " (" + statusMessage + ")<br/>" +
				"<b>" + constants.serviceErrorContent() + "</b>:<br/>" + text));
	}

	public void parseError(String text) {
		ErrorResponseDecoder decoder = new ErrorResponseDecoder();
		decoder.parse(text);
		if (!decoder.errorsEncountered()) {
			ErrorResponse serviceError = decoder.getResult();
			if (serviceError.isAuthError()) {
				eventBus.fireEvent(new AuthenticationEvent(AuthenticationEvent.EventType.ERROR));
			} else {
				eventBus.fireEvent(new ErrorDisplayEvent(constants.serviceError() + " " + serviceError.message, serviceError.trace));
			}
		} else {
			GWT.log("[parseError()]", null);
			/* unexpected format */
			eventBus.fireEvent(new ErrorDisplayEvent(constants.serviceError() + " " + constants.unknownFormat(),
					"<b>" + constants.serviceErrorUrl() + "</b>: " + URL + "<br/>" +
					"<b>" + constants.serviceErrorContent() + "</b>:<br/>"));
		}
	}


}
