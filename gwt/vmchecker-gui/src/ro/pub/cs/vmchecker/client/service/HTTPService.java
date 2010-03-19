package ro.pub.cs.vmchecker.client.service;

import java.util.HashMap;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.user.client.rpc.AsyncCallback; 

import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.model.AuthenticationResponse;
import ro.pub.cs.vmchecker.client.model.Course;
import ro.pub.cs.vmchecker.client.model.Result;
import ro.pub.cs.vmchecker.client.service.json.AssignmentsListDecoder;
import ro.pub.cs.vmchecker.client.service.json.AuthenticationResponseDecoder;
import ro.pub.cs.vmchecker.client.service.json.CoursesListDecoder;
import ro.pub.cs.vmchecker.client.service.json.NullDecoder;
import ro.pub.cs.vmchecker.client.service.json.ResultDecoder;

public class HTTPService {
	
	public static final String VMCHECKER_SERVICES_URL = GWT.getHostPageBaseURL() + "services/"; 
	public static final String GET_COURSES_URL = VMCHECKER_SERVICES_URL + "getCourses.json";
	public static final String GET_ASSIGNMENTS_URL = VMCHECKER_SERVICES_URL + "getAssignments.php";
	public static final String GET_RESULTS_URL = VMCHECKER_SERVICES_URL + "getResults.php";
	public static final String PERFORM_AUTHENTICATION_URL = VMCHECKER_SERVICES_URL + "auth.php";
	public static final String LOGOUT_URL = VMCHECKER_SERVICES_URL + "logout.php"; 
	public static final String UPLOAD_URL = VMCHECKER_SERVICES_URL + "upload.php"; 
	
	private HandlerManager eventBus; 
	
	public HTTPService(HandlerManager eventBus) {
		this.eventBus = eventBus; 
	}
	
	public void getCourses(final AsyncCallback<Course[]> callback) {
		Delegate<Course[]> delegate = new Delegate<Course[]>(eventBus, GET_COURSES_URL, true);
		delegate.sendRequest(callback, new CoursesListDecoder(), null); 
	}
	
	public void getAssignments(String courseId, final AsyncCallback<Assignment[]> callback) {
		Delegate<Assignment[]> delegate = new Delegate<Assignment[]>(eventBus, GET_ASSIGNMENTS_URL, true); 
		HashMap<String, String> params = new HashMap<String, String>();
		params.put("courseId", courseId);
		delegate.sendRequest(callback, new AssignmentsListDecoder(), params); 
	}
	
	public void getResults(String courseId, String assignmentId, final AsyncCallback<Result> callback) {
		Delegate<Result> delegate = new Delegate<Result>(eventBus, GET_RESULTS_URL, true);
		HashMap<String, String> params = new HashMap<String, String>(); 
		params.put("courseId", courseId);  
		params.put("assignmentId", assignmentId); 
		delegate.sendRequest(callback, new ResultDecoder(), params); 
	}
	
	public void performAuthentication(String username, String password, final AsyncCallback<AuthenticationResponse> callback) {
		Delegate<AuthenticationResponse> delegate = new Delegate<AuthenticationResponse>(eventBus, PERFORM_AUTHENTICATION_URL, false);
		HashMap<String, String> params = new HashMap<String, String>(); 
		params.put("username", username);  
		params.put("password", password); 
		delegate.sendRequest(callback, new AuthenticationResponseDecoder(), params); 
	}
	
	public void sendLogoutRequest(final AsyncCallback<Boolean> callback) {
		Delegate<Boolean> delegate = new Delegate<Boolean>(eventBus, LOGOUT_URL, true);
		delegate.sendRequest(callback, new NullDecoder(), null); 
	}

}
