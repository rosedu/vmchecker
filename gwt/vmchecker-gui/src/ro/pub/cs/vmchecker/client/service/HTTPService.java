package ro.pub.cs.vmchecker.client.service;

import java.util.HashMap;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.user.client.rpc.AsyncCallback; 

import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.model.AuthenticationResponse;
import ro.pub.cs.vmchecker.client.model.Course;
import ro.pub.cs.vmchecker.client.model.EvaluationResult;
import ro.pub.cs.vmchecker.client.model.StudentInfo;
import ro.pub.cs.vmchecker.client.service.json.AssignmentsListDecoder;
import ro.pub.cs.vmchecker.client.service.json.AuthenticationResponseDecoder;
import ro.pub.cs.vmchecker.client.service.json.CoursesListDecoder;
import ro.pub.cs.vmchecker.client.service.json.NullDecoder;
import ro.pub.cs.vmchecker.client.service.json.ResultDecoder;
import ro.pub.cs.vmchecker.client.service.json.StatisticsDecoder;

public class HTTPService {
	
	private static final String SERVICES_SUFFIX = "services/services.py"; 
	public static String VMCHECKER_SERVICES_URL = computeServicesURL(); 
	public static String GET_COURSES_URL = VMCHECKER_SERVICES_URL + "getCourses";
	public static String GET_ASSIGNMENTS_URL = VMCHECKER_SERVICES_URL + "getAssignments";
	public static String GET_USER_RESULTS_URL = VMCHECKER_SERVICES_URL + "getUserResults";	
	public static String GET_ALL_RESULTS_URL = VMCHECKER_SERVICES_URL + "getAllGrades";	
	public static String GET_RESULTS_URL = VMCHECKER_SERVICES_URL + "getResults";
	public static String PERFORM_AUTHENTICATION_URL = VMCHECKER_SERVICES_URL + "login";
	public static String LOGOUT_URL = VMCHECKER_SERVICES_URL + "logout"; 
	public static String UPLOAD_URL = VMCHECKER_SERVICES_URL + "uploadAssignment"; 
	
	/**
	 * Computes the base URL for services by erasing the last level 
	 * of directories from the URL and add the SERVICES_SUFFIX to it 
	 * For example, if the UI is loaded on 
	 * http://vmchecker.cs.pub.ro/vmchecker/ui/Vmchecker.html
	 * the services URL will be: 
	 * http://vmchecker.cs.pub.ro/vmchecker/<SERVICES_SUFFIX>/
	 * @return the base URL for vmchecker services 
	 */
	public static String computeServicesURL() {
		String uiURL = GWT.getHostPageBaseURL(); 
		return uiURL.substring(0, uiURL.substring(0, uiURL.lastIndexOf('/')).lastIndexOf('/') + 1) + SERVICES_SUFFIX + '/'; 		
	}
	
	private HandlerManager eventBus; 
	
	public HTTPService(HandlerManager eventBus) {
		this.eventBus = eventBus;
	}
	
	public void getCourses(final AsyncCallback<Course[]> callback) {
		Delegate<Course[]> delegate = new Delegate<Course[]>(eventBus, GET_COURSES_URL, true);
		delegate.sendRequest(callback, new CoursesListDecoder(), null); 
	}
	
	public void getAssignments(String courseId, final AsyncCallback<Assignment[]> callback) {
		Delegate<Assignment[]> delegate = 
			new Delegate<Assignment[]>(eventBus, GET_ASSIGNMENTS_URL, true); 
		HashMap<String, String> params = new HashMap<String, String>();
		params.put("courseId", courseId);
		delegate.sendRequest(callback, new AssignmentsListDecoder(), params); 
	}
	
	public void getResults(String courseId, String assignmentId, 
			final AsyncCallback<EvaluationResult[]> callback) {
		Delegate<EvaluationResult[]> delegate = 
			new Delegate<EvaluationResult[]>(eventBus, GET_RESULTS_URL, true);
		HashMap<String, String> params = new HashMap<String, String>(); 
		params.put("courseId", courseId);  
		params.put("assignmentId", assignmentId); 
		delegate.sendRequest(callback, new ResultDecoder(), params); 
	}

	public void getUserResults(String courseId, String assignmentId, String username, 
			final AsyncCallback<EvaluationResult[]> callback) {
		Delegate<EvaluationResult[]> delegate = 
			new Delegate<EvaluationResult[]>(eventBus, GET_USER_RESULTS_URL, true);
		HashMap<String, String> params = new HashMap<String, String>(); 
		params.put("courseId", courseId);  
		params.put("assignmentId", assignmentId);
		params.put("username", username); 
		delegate.sendRequest(callback, new ResultDecoder(), params); 
	}
	
	public void getAllResults(String courseId, final AsyncCallback<StudentInfo[]> callback) {
		Delegate<StudentInfo[]> delegate = 
			new Delegate<StudentInfo[]>(eventBus, GET_ALL_RESULTS_URL, true); 
		HashMap<String, String> params = new HashMap<String, String>(); 
		params.put("courseId", courseId);  
		delegate.sendRequest(callback, new StatisticsDecoder(), params); 		
	}
	
	public void performAuthentication(String username, String password, 
			final AsyncCallback<AuthenticationResponse> callback) {
		Delegate<AuthenticationResponse> delegate = 
			new Delegate<AuthenticationResponse>(eventBus, PERFORM_AUTHENTICATION_URL, false);
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
