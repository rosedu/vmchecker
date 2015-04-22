package ro.pub.cs.vmchecker.client.service;

import java.util.HashMap;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.http.client.Request;

import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.model.AccountType;
import ro.pub.cs.vmchecker.client.model.AuthenticationResponse;
import ro.pub.cs.vmchecker.client.model.Course;
import ro.pub.cs.vmchecker.client.model.EvaluationResult;
import ro.pub.cs.vmchecker.client.model.Md5Status;
import ro.pub.cs.vmchecker.client.model.FileList;
import ro.pub.cs.vmchecker.client.model.ResultInfo;
import ro.pub.cs.vmchecker.client.service.json.AssignmentsListDecoder;
import ro.pub.cs.vmchecker.client.service.json.AuthenticationResponseDecoder;
import ro.pub.cs.vmchecker.client.service.json.CoursesListDecoder;
import ro.pub.cs.vmchecker.client.service.json.NullDecoder;
import ro.pub.cs.vmchecker.client.service.json.ResultDecoder;
import ro.pub.cs.vmchecker.client.service.json.Md5StatusDecoder;
import ro.pub.cs.vmchecker.client.service.json.FileListDecoder;
import ro.pub.cs.vmchecker.client.service.json.StatisticsDecoder;

public class HTTPService {

	private static final String SERVICES_SUFFIX = "services/services.py";
	public static String VMCHECKER_SERVICES_URL = computeServicesURL();
	public static String GET_COURSES_URL = VMCHECKER_SERVICES_URL + "getCourses";
	public static String GET_ASSIGNMENTS_URL = VMCHECKER_SERVICES_URL + "getAssignments";
	public static String GET_TEAM_RESULTS_URL = VMCHECKER_SERVICES_URL + "getTeamResults";
	public static String GET_USER_RESULTS_URL = VMCHECKER_SERVICES_URL + "getUserResults";
	public static String GET_UPLOADED_MD5_URL = VMCHECKER_SERVICES_URL + "getUploadedMd5";
	public static String GET_ALL_RESULTS_URL = VMCHECKER_SERVICES_URL + "getAllGrades";
	public static String GET_STORAGE_FILE_LIST_URL = VMCHECKER_SERVICES_URL + "getStorageDirContents";
	public static String PERFORM_AUTHENTICATION_URL = VMCHECKER_SERVICES_URL + "login";
	public static String LOGOUT_URL = VMCHECKER_SERVICES_URL + "logout";
	public static String UPLOAD_URL = VMCHECKER_SERVICES_URL + "uploadAssignment";
	public static String UPLOAD_MD5_URL = VMCHECKER_SERVICES_URL + "uploadAssignmentMd5";
	public static String BEGIN_EVALUATION_URL = VMCHECKER_SERVICES_URL + "beginEvaluation";

	private EventBus eventBus;
	private HashMap<String, Request> ongoingRequests = new HashMap<String, Request>();

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

	public HTTPService(EventBus eventBus) {
		this.eventBus = eventBus;
	}

	public void getCourses(final AsyncCallback<Course[]> callback) {
		Delegate<Course[]> delegate = new Delegate<Course[]>(eventBus, GET_COURSES_URL, true, false, ongoingRequests);
		delegate.sendRequest(callback, new CoursesListDecoder(), null);
	}

	public void getAssignments(String courseId, final AsyncCallback<Assignment[]> callback) {
		Delegate<Assignment[]> delegate =
			new Delegate<Assignment[]>(eventBus, GET_ASSIGNMENTS_URL, true, false, ongoingRequests);
		HashMap<String, String> params = new HashMap<String, String>();
		params.put("courseId", courseId);
		delegate.sendRequest(callback, new AssignmentsListDecoder(), params);
	}

	public void getUploadedMd5(String courseId, String assignmentId,
			final AsyncCallback<Md5Status> callback) {
		Delegate<Md5Status> delegate =
			new Delegate<Md5Status>(eventBus, GET_UPLOADED_MD5_URL, true, false, ongoingRequests);
		HashMap<String, String> params = new HashMap<String, String>();
		params.put("courseId", courseId);
		params.put("assignmentId", assignmentId);
		delegate.sendRequest(callback, new Md5StatusDecoder(), params);
	}

	public void getStorageDirContents(String courseId, String assignmentId,
			final AsyncCallback<FileList> callback) {
		Delegate<FileList> delegate =
			new Delegate<FileList>(eventBus, GET_STORAGE_FILE_LIST_URL, true, false, ongoingRequests);
		HashMap<String, String> params = new HashMap<String, String>();
		params.put("courseId", courseId);
		params.put("assignmentId", assignmentId);
		delegate.sendRequest(callback, new FileListDecoder(), params);
	}

	public void getResults(String courseId, String assignmentId,
			String account, AccountType accountType,
			final AsyncCallback<EvaluationResult[]> callback) {
		final String URL = accountType == AccountType.USER ? GET_USER_RESULTS_URL : GET_TEAM_RESULTS_URL;
		Delegate<EvaluationResult[]> delegate =
			new Delegate<EvaluationResult[]>(eventBus, URL, true, true, ongoingRequests);
		HashMap<String, String> params = new HashMap<String, String>();
		params.put("courseId", courseId);
		params.put("assignmentId", assignmentId);
		/*
		 * If no account is given, the current logged in account will be used implicitly.
		 */
		if (account != null) {
			if (accountType == AccountType.USER) {
				params.put("username", account);
			} else {
				params.put("teamname", account);
			}
		}
		delegate.sendRequest(callback, new ResultDecoder(), params);
	}

	public void getAllResults(String courseId, final AsyncCallback<ResultInfo[]> callback) {
		Delegate<ResultInfo[]> delegate =
			new Delegate<ResultInfo[]>(eventBus, GET_ALL_RESULTS_URL, true, false, ongoingRequests);
		HashMap<String, String> params = new HashMap<String, String>();
		params.put("courseId", courseId);
		delegate.sendRequest(callback, new StatisticsDecoder(), params);
	}

	public void performAuthentication(String username, String password, Boolean extendSession,
			final AsyncCallback<AuthenticationResponse> callback) {
		Delegate<AuthenticationResponse> delegate =
			new Delegate<AuthenticationResponse>(eventBus, PERFORM_AUTHENTICATION_URL, false, true, ongoingRequests);
		HashMap<String, String> params = new HashMap<String, String>();
		params.put("username", username);
		params.put("password", password);
		params.put("remember_me", extendSession.toString());
		delegate.sendRequest(callback, new AuthenticationResponseDecoder(), params);
	}

	public void sendLogoutRequest(final AsyncCallback<Boolean> callback) {
		Delegate<Boolean> delegate = new Delegate<Boolean>(eventBus, LOGOUT_URL, true, false, ongoingRequests);
		delegate.sendRequest(callback, new NullDecoder(), null);
	}

}
