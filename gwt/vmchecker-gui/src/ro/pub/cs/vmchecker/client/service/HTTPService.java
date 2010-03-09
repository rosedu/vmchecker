package ro.pub.cs.vmchecker.client.service;

import java.util.HashMap;
import java.util.Iterator;

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
import ro.pub.cs.vmchecker.client.service.json.AssignmentsListDecoder;
import ro.pub.cs.vmchecker.client.service.json.CoursesListDecoder;

public class HTTPService {
	
	public static final String VMCHECKER_SERVICES_URL = GWT.getHostPageBaseURL() + "services/"; 
	public static final String UPLOAD_URL = VMCHECKER_SERVICES_URL + "upload.php"; 
	
	public static String packParameters(HashMap<String, String> params) {
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
	
	public void getAssignments(String courseId, final AsyncCallback<Assignment[]> callback) {
		HashMap<String, String> params = new HashMap<String, String>(); 
		params.put("courseId", courseId); 
		RequestBuilder rb = new RequestBuilder(RequestBuilder.GET, VMCHECKER_SERVICES_URL + "getAssignments.php?" + packParameters(params));
		rb.setCallback(new RequestCallback() {

			public void onError(Request request, Throwable exception) {
				callback.onFailure(exception);
			}

			public void onResponseReceived(Request request, Response response) {
				AssignmentsListDecoder decoder = new AssignmentsListDecoder(); 
				try {
					Assignment[] assignments = decoder.decode(response.getText());
					callback.onSuccess(assignments); 
				} catch (JSONException e) {
					callback.onFailure(e); 
				}
			}
		}); 
		GWT.log("Debug: " + packParameters(params), null); 
		try {
			rb.send(); 
		} catch (RequestException e) {
			GWT.log("HTTPService: ", e);
		}
	}
}
