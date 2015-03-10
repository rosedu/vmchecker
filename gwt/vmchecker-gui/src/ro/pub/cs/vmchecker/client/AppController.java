package ro.pub.cs.vmchecker.client;

import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;

import ro.pub.cs.vmchecker.client.event.AuthenticationEvent;
import ro.pub.cs.vmchecker.client.event.AuthenticationEventHandler;
import ro.pub.cs.vmchecker.client.event.CourseSelectedEvent;
import ro.pub.cs.vmchecker.client.event.CourseSelectedEventHandler;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent;
import ro.pub.cs.vmchecker.client.model.Course;
import ro.pub.cs.vmchecker.client.presenter.AssignmentPresenter;
import ro.pub.cs.vmchecker.client.presenter.StatusPresenter;
import ro.pub.cs.vmchecker.client.presenter.HeaderPresenter;
import ro.pub.cs.vmchecker.client.presenter.LoginPresenter;
import ro.pub.cs.vmchecker.client.presenter.Presenter;
import ro.pub.cs.vmchecker.client.service.HTTPService;
import ro.pub.cs.vmchecker.client.ui.AssignmentWidget;
import ro.pub.cs.vmchecker.client.ui.StatusWidget;
import ro.pub.cs.vmchecker.client.ui.HeaderWidget;
import ro.pub.cs.vmchecker.client.ui.LoginWidget;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.logical.shared.ValueChangeEvent;
import com.google.gwt.event.logical.shared.ValueChangeHandler;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.HistoryListener;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.SimplePanel;


public class AppController implements HistoryListener {
	
	private EventBus eventBus;
	private HTTPService service; 
	private HasWidgets container;
	private SimplePanel content = new SimplePanel(); 
	private Presenter mainPresenter = null; 
	private HeaderPresenter headerPresenter = null; 
	private LoginPresenter loginPresenter = null; 
	private StatusPresenter statusPresenter = null;
	
	private ArrayList<Course> courses; 
	private HashSet<String> coursesTags;
	private HashMap<String, Course> idToCourse; 
	
	public AppController(EventBus eventBus, HTTPService service) {
		this.eventBus = eventBus;
		this.service = service; 
		bindHistory();
		listenCourseChange();
		listenAuthenticationEvents(); 
	}
	
	private void listenAuthenticationEvents() {
		eventBus.addHandler(AuthenticationEvent.TYPE, new AuthenticationEventHandler() {

			@Override
			public void onAuthenticationChange(AuthenticationEvent event) {
				GWT.log("Authentication event received", null); 
				if (event.getType() == AuthenticationEvent.EventType.SUCCESS) {
					CookieManager.saveUser(event.getUser());
					displayContent(); 
				} else if (event.getType() == AuthenticationEvent.EventType.ERROR) {
					/*
					 * Reset status bar when the user is logged out.
					 */
					eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.RESET, null));
					CookieManager.clearCookies();
					displayLogin(); 
				}
			}
		}); 
	}

	private void listenCourseChange() {
		eventBus.addHandler(CourseSelectedEvent.TYPE, new CourseSelectedEventHandler(){
			public void onSelect(CourseSelectedEvent event) {
				CookieManager.saveLastCourse(event.getCourseId()); 
				History.newItem(event.getCourseId()); 
			}			
		}); 
	}
	
	public void go(final HasWidgets container) {
		this.container = container;
		/* initialize status presenter */
		statusPresenter = new StatusPresenter(eventBus, service, 
					new StatusWidget());
		/*
		 * Assume user's already logged in. If that's not the case,
		 * the HTTPService will return an Authenthication Error
		 * prompting the login page.
		 */
		displayContent(); 
	}

	private void clearContainer() {
		/* The status bar should be present even after clearing the container. */
		container.clear();
		statusPresenter.go(container);
	}
	
	private void displayLogin() {
		loginPresenter = new LoginPresenter(eventBus, service, new LoginWidget());
		clearContainer();
		History.newItem("", false); 
		loginPresenter.go(container); 
	}
	
	private void displayContent() {
		GWT.log("[displayContent()] entering in function", null); 
		clearContainer();
		service.getCourses(new AsyncCallback<Course[]>() {

			@Override
			public void onFailure(Throwable caught) {
				GWT.log("[displayContent.onFailure()]", caught); 
				Window.alert(caught.getMessage()); 
			}

			@Override
			public void onSuccess(Course[] result) {
				courses = new ArrayList<Course>(); 
				coursesTags = new HashSet<String>();
				idToCourse = new HashMap<String, Course>(); 
				
				for (int i = 0; i < result.length; i++) {
					Course course = result[i]; 
					coursesTags.add(course.id);
					idToCourse.put(course.id, course);
					courses.add(course); 
				}
				
				/* initialize header presenter */
				headerPresenter = new HeaderPresenter(eventBus, service, 
						new HeaderWidget(CookieManager.getUser()));
				headerPresenter.setCourses(courses); 
				 
				headerPresenter.go(container); 
				headerPresenter.selectCourse(courses.get(0).id);
				/* add the content container */
				container.add(content); 
				/* initialize history entries */
				if ("".equals(History.getToken())) {
					String defaultCourse = null; 
					String lastCourse = CookieManager.getLastCourse(); 
					if (lastCourse != null && coursesTags.contains(lastCourse)) {
						defaultCourse = lastCourse; 
					} else {
						defaultCourse = courses.get(0).id; 
					}
					History.newItem(defaultCourse);
				} else {
					History.fireCurrentHistoryState(); 
				}
			}			
		}); 		
	}
	/**
	 * This method handles changes in application's state defined by a 
	 * certain browser history entry 
	 */
	public void onHistoryChanged(String token) {
		if (token != null) {			
			if (!token.isEmpty() && coursesTags.contains(token)) {
				if (mainPresenter != null) {
					mainPresenter.clearEventHandlers(); 
				}
				mainPresenter = new AssignmentPresenter(eventBus, service, idToCourse.get(token).id, CookieManager.getUser(), new AssignmentWidget());
				headerPresenter.selectCourse(idToCourse.get(token).id); 
			} else {
				token = courses.get(0).id;
				History.newItem(token);
				return; 				
			}
			
			if (mainPresenter != null) {
				content.clear();
				mainPresenter.go(content); 
			}
		}
	}
	
	private void bindHistory() {
		History.addHistoryListener(this);
	}
}
