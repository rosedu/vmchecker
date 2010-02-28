package ro.pub.cs.vmchecker.client.service;

import com.google.gwt.core.client.GWT;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.json.client.JSONException;
import com.google.gwt.user.client.rpc.AsyncCallback; 

import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.model.Course;
import ro.pub.cs.vmchecker.client.service.json.CoursesListDecoder;

public class HTTPService {
	
	public static final String VMCHECKER_SERVICES_URL = GWT.getHostPageBaseURL() + "services/"; 
	
	public void getCourses(final AsyncCallback<Course[]> callback) {
		GWT.log("base URL: " + VMCHECKER_SERVICES_URL, null); 
		RequestBuilder rb = new RequestBuilder(RequestBuilder.GET, VMCHECKER_SERVICES_URL + "getCourses.json");
		rb.setCallback(new RequestCallback() {
			public void onError(Request request, Throwable exception) {
				callback.onFailure(exception); 
			}

			public void onResponseReceived(Request request, Response response) {
				CoursesListDecoder decoder = new CoursesListDecoder();
				try {
					Course[] courses = decoder.decode(response.getText());
					callback.onSuccess(courses); 
				} catch (JSONException e) {
					callback.onFailure(e); 
				}
			}			
		}); 
		try {
			rb.send(); 
		} catch (RequestException e) {
			GWT.log("HTTPService: ", e); 
		}
	}
	
	public void getAssignments(String courseId, AsyncCallback<Assignment[]> callback) {
		
	}
}
