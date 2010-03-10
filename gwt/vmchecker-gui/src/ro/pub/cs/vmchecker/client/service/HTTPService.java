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
import ro.pub.cs.vmchecker.client.model.AuthenticationResponse;
import ro.pub.cs.vmchecker.client.model.Course;
import ro.pub.cs.vmchecker.client.model.Result;
import ro.pub.cs.vmchecker.client.service.json.AssignmentsListDecoder;
import ro.pub.cs.vmchecker.client.service.json.AuthenticationResponseDecoder;
import ro.pub.cs.vmchecker.client.service.json.CoursesListDecoder;
import ro.pub.cs.vmchecker.client.service.json.ResultDecoder;

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
			callback.onFailure(e);  
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
		try {
			rb.send(); 
		} catch (RequestException e) {
			callback.onFailure(e); 
		}
	}
	
	public void getResults(String courseId, String assignmentId, final AsyncCallback<Result> callback) {
		HashMap<String, String> params = new HashMap<String, String>(); 
		params.put("courseId", courseId);  
		params.put("assignmentId", assignmentId); 
		RequestBuilder rb = new RequestBuilder(RequestBuilder.GET, VMCHECKER_SERVICES_URL + "getResults.php?" + packParameters(params));
		rb.setCallback(new RequestCallback() {

			public void onError(Request request, Throwable exception) {
				callback.onFailure(exception);
			}

			public void onResponseReceived(Request request, Response response) {
				ResultDecoder decoder = new ResultDecoder();
				try {
					Result result = decoder.decode(response.getText());
					callback.onSuccess(result); 
				} catch (JSONException e) {
					callback.onFailure(e); 
				}
			}
		});
		try {
			rb.send(); 
		} catch (RequestException e) {
			callback.onFailure(e); 
		}
		
	}
	
	public void checkAuthentication(final AsyncCallback<AuthenticationResponse> callback) {
		RequestBuilder rb = new RequestBuilder(RequestBuilder.GET, VMCHECKER_SERVICES_URL + "checkAuth.php");
		rb.setCallback(new RequestCallback() {

			@Override
			public void onError(Request request, Throwable exception) {
				callback.onFailure(exception); 
			}

			@Override
			public void onResponseReceived(Request request, Response response) {
				AuthenticationResponseDecoder decoder = new AuthenticationResponseDecoder(); 
				try {
					AuthenticationResponse authResponse = decoder.decode(response.getText());
					callback.onSuccess(authResponse); 
				} catch (JSONException e) {
					callback.onFailure(e); 
				}
			}
		}); 
		try {
			rb.send(); 
		} catch (RequestException e) {
			callback.onFailure(e); 
		}		
	}
	
	public void performAuthentication(String username, String password, final AsyncCallback<AuthenticationResponse> callback) {
		RequestBuilder rb = new RequestBuilder(RequestBuilder.POST, VMCHECKER_SERVICES_URL + "auth.php"); 
		HashMap<String, String> params = new HashMap<String, String>(); 
		params.put("username", username);  
		params.put("password", password); 
		rb.setRequestData(packParameters(params));
		rb.setHeader("Content-Type", "application/x-www-form-urlencoded"); 
		rb.setCallback(new RequestCallback() {

			@Override
			public void onError(Request request, Throwable exception) {
				callback.onFailure(exception); 
			}

			@Override
			public void onResponseReceived(Request request, Response response) {
				AuthenticationResponseDecoder decoder = new AuthenticationResponseDecoder(); 
				try {
					AuthenticationResponse authResponse = decoder.decode(response.getText());
					callback.onSuccess(authResponse); 
				} catch (JSONException e) {
					callback.onFailure(e); 
				}				
			}	
		}); 
		try {
			rb.send(); 
		} catch (RequestException e) {
			callback.onFailure(e); 
		}			
	}

	public void sendLogoutRequest(final AsyncCallback<Boolean> callback) {
		RequestBuilder rb = new RequestBuilder(RequestBuilder.POST, VMCHECKER_SERVICES_URL + "logout.php"); 
		rb.setCallback(new RequestCallback() {

			@Override
			public void onError(Request request, Throwable exception) {
				callback.onFailure(exception); 
			}

			@Override
			public void onResponseReceived(Request request, Response response) {
				callback.onSuccess(new Boolean(true)); 
			}	
		}); 
		try {
			rb.send(); 
		} catch (RequestException e) {
			callback.onFailure(e); 
		}			
	}
	
}
