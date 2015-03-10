package ro.pub.cs.vmchecker.client.service;

import java.util.HashMap;
import java.util.Iterator;

import ro.pub.cs.vmchecker.client.event.AuthenticationEvent;
import ro.pub.cs.vmchecker.client.event.ErrorDisplayEvent;
import ro.pub.cs.vmchecker.client.model.ErrorResponse;
import ro.pub.cs.vmchecker.client.service.ServiceError;
import ro.pub.cs.vmchecker.client.service.json.ErrorResponseDecoder;
import ro.pub.cs.vmchecker.client.service.json.JSONDecoder;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.http.client.URL;
import com.google.gwt.i18n.client.LocaleInfo;

public class Delegate<T> {

	public static final int requestTimeoutMillis = 10000; /* 10 seconds */

	private EventBus eventBus;
	private RequestBuilder rb;
	private boolean isGet, attachLocale;
	private String url;
	private HashMap<String, Request> ongoingRequests;

	public Delegate(EventBus eventBus, String url, boolean isGet, boolean attachLocale,
			HashMap<String, Request> ongoingRequests) {
		this.eventBus = eventBus;
		this.isGet = isGet;
		this.attachLocale = attachLocale;
		this.url = url;
		this.ongoingRequests = ongoingRequests;
		/**
		 * We reconstruct the entire RequestBuilder for GET requests when
		 * we call sendRequest(), so don't create a new instance for it
		 * here.
		 */
		if (!isGet) {
			rb = new RequestBuilder(RequestBuilder.POST, url);
			rb.setHeader("Content-Type", "application/x-www-form-urlencoded");
			rb.setTimeoutMillis(requestTimeoutMillis);
		}

		Request ongoing = ongoingRequests.get(url);
		if (ongoing != null) ongoing.cancel();

	}

	private String packParameters(HashMap<String, String> params) {
		StringBuffer result = new StringBuffer();
		for (Iterator<String> it = params.keySet().iterator(); it.hasNext(); ) {
			String key = it.next();
			result.append(URL.encodeComponent(key, true) + "=" + URL.encodeComponent(params.get(key), true));
			if (it.hasNext()) {
				result.append('&');
			}
		}

		if (attachLocale) {
			result.append('&');
			result.append(URL.encodeComponent("locale", true) + "=" +
				URL.encodeComponent(LocaleInfo.getCurrentLocale().getLocaleName(), true));
		}

		return result.toString();
	}

	public void sendRequest(final AsyncCallback<T> callback, final JSONDecoder<T> decoder, HashMap<String, String> params) {

		RequestCallback rqc = new RequestCallback() {

			public void onError(Request request, Throwable exception) {
				callback.onFailure(exception);
			}

			public void onResponseReceived(Request request, Response response) {
				ServiceError se = new ServiceError(eventBus, url);

				if (response.getStatusCode() != Response.SC_OK) {
					GWT.log("Wrong response returned by server.", null);
					se.serverError(response.getStatusCode(), response.getStatusText(), response.getText());
					return;
				}

				decoder.parse(response.getText());
				if (decoder.errorsEncountered()) {
					GWT.log("Decoder could not parse response.", null);
					se.parseError(response.getText());
				} else {
					T result = decoder.getResult();
					callback.onSuccess(result);
				}
			}
		};

		String packedParameters = null;
		if(params != null) packedParameters = packParameters(params);

		if (isGet) {
			rb = new RequestBuilder(RequestBuilder.GET, url + "?" + packedParameters);
			rb.setHeader("Content-Type", "application/x-www-form-urlencoded");
			rb.setTimeoutMillis(requestTimeoutMillis);
		}

		try {
			/*
			 * Changed from send() to sendRequest() because sendRequest() doesn't cache,
			 * or at least so is said in the GWT documentation. Given the nature of the
			 * different requests this seems more appropriate
			 */
			Request req = rb.sendRequest(packedParameters, rqc);
			ongoingRequests.put(url, req);
		} catch(RequestException e) {
			callback.onFailure(e);
		}
	}


}
