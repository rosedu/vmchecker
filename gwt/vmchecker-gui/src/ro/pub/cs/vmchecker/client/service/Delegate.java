package ro.pub.cs.vmchecker.client.service;

import java.util.HashMap;
import java.util.Iterator;

import ro.pub.cs.vmchecker.client.event.AuthenticationEvent;
import ro.pub.cs.vmchecker.client.event.ErrorDisplayEvent;
import ro.pub.cs.vmchecker.client.model.ErrorResponse;
import ro.pub.cs.vmchecker.client.service.json.ErrorResponseDecoder;
import ro.pub.cs.vmchecker.client.service.json.JSONDecoder;

import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;

public class Delegate<T> {
	
	private HandlerManager eventBus; 
	private RequestBuilder rb; 
	private boolean isGet;
	private String URL; 
	
	public Delegate(HandlerManager eventBus, String URL, boolean isGet) {
		this.eventBus = eventBus;
		this.isGet = isGet;
		this.URL = URL; 
		if (isGet) {
			rb = new RequestBuilder(RequestBuilder.GET, URL);
		} else {
			rb = new RequestBuilder(RequestBuilder.POST, URL);
		}
		rb.setHeader("Content-Type", "application/x-www-form-urlencoded"); 
	}
	
	private String packParameters(HashMap<String, String> params) {
		StringBuffer result = new StringBuffer();  
		for (Iterator<String> it = params.keySet().iterator(); it.hasNext(); ) {
			String key = it.next(); 
			result.append(key + "=" + params.get(key));
			if (it.hasNext()) {
				result.append('&'); 
			}
		}
		return result.toString();  		
	}

	public void parseError(AsyncCallback<T> callback, String text) {
		try {
			ErrorResponseDecoder decoder = new ErrorResponseDecoder(); 
			ErrorResponse serviceError = decoder.decode(text);
			if (serviceError.isAuthError()) {
				eventBus.fireEvent(new AuthenticationEvent(AuthenticationEvent.EventType.ERROR));  
			} else {
				eventBus.fireEvent(new ErrorDisplayEvent("[Service Error]" + serviceError.message, serviceError.trace)); 
			}
		} catch (Exception e) { 
			callback.onFailure(e);
			Window.alert(e.getMessage());
		}
	}
		
	public void sendRequest(final AsyncCallback<T> callback, final JSONDecoder<T> decoder, HashMap<String, String> params) {
		if (params != null) {
			if (isGet) {
				rb = new RequestBuilder(RequestBuilder.GET, URL + "?" + packParameters(params)); 
			} else {
				rb.setRequestData(packParameters(params));
			}
		}
		rb.setCallback(new RequestCallback() {
			public void onError(Request request, Throwable exception) {
				callback.onFailure(exception); 
			}

			public void onResponseReceived(Request request, Response response) {
				try {
					T result = decoder.decode(response.getText()); 
					callback.onSuccess(result); 
				} catch (Exception e) {
					parseError(callback, response.getText()); 
				}
			}			
		}); 
		try {
			rb.send(); 
		} catch (RequestException e) {
			callback.onFailure(e);  
		}
	}
	
	
}
