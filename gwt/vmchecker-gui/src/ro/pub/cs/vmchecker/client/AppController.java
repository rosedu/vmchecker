package ro.pub.cs.vmchecker.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

import ro.pub.cs.vmchecker.client.event.AuthenticationEvent;
import ro.pub.cs.vmchecker.client.event.AuthenticationEventHandler;
import ro.pub.cs.vmchecker.client.event.CourseSelectedEvent;
import ro.pub.cs.vmchecker.client.event.CourseSelectedEventHandler;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent;
import ro.pub.cs.vmchecker.client.model.AuthenticationResponse;
import ro.pub.cs.vmchecker.client.model.Course;
import ro.pub.cs.vmchecker.client.presenter.AssignmentPresenter;
import ro.pub.cs.vmchecker.client.presenter.HeaderPresenter;
import ro.pub.cs.vmchecker.client.presenter.LoginPresenter;
import ro.pub.cs.vmchecker.client.presenter.Presenter;
import ro.pub.cs.vmchecker.client.service.HTTPService;
import ro.pub.cs.vmchecker.client.ui.AssignmentWidget;
import ro.pub.cs.vmchecker.client.ui.HeaderWidget;
import ro.pub.cs.vmchecker.client.ui.LoginWidget;


import com.google.gwt.core.client.GWT;
import com.google.gwt.event.logical.shared.ValueChangeEvent;
import com.google.gwt.event.logical.shared.ValueChangeHandler;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.SimplePanel;


public class AppController implements ValueChangeHandler<String> {
	
	private HandlerManager eventBus;
	private HTTPService service; 
	private HasWidgets container;
	private SimplePanel content = new SimplePanel(); 
	private Presenter mainPresenter = null; 
	private HeaderPresenter headerPresenter = null; 
	private LoginPresenter loginPresenter = null; 
	
	private ArrayList<Course> courses; 
	private HashSet<String> coursesTags;
	private HashMap<String, Course> idToCourse; 
	private String selectedCourseId; 
	
	public AppController(HandlerManager eventBus, HTTPService service) {
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
				if (event.getType() == AuthenticationEvent.EventType.SUCCESS) {
					displayContent(event.getUsername()); 
				} else if (event.getType() == AuthenticationEvent.EventType.FORCE_CHECK) {
					checkAuthentication(); 
				}
			}
		}); 
	}

	private void listenCourseChange() {
		eventBus.addHandler(CourseSelectedEvent.TYPE, new CourseSelectedEventHandler(){
			public void onSelect(CourseSelectedEvent event) {
				History.newItem(event.getCourseId()); 
			}			
		}); 
	}
	
	private void selectCourse(String courseId) {
		selectedCourseId = courseId;
		headerPresenter.selectCourse(courses.get(0).id);
	}
	
	public void go(final HasWidgets container) {
		this.container = container;
		checkAuthentication(); 
	}
	
	private void checkAuthentication() {
		service.checkAuthentication(new AsyncCallback<AuthenticationResponse>() {

			@Override
			public void onFailure(Throwable caught) {
				GWT.log("Error in checking authentication", caught); 
				displayLogin(); 
			}

			@Override
			public void onSuccess(AuthenticationResponse response) {
				if (response.status) {
					displayContent(response.username); 
				} else {
					GWT.log("Not authenticated", null); 
					displayLogin(); 
				}
			}
		}); 
	}
	
	private void displayLogin() {
		loginPresenter = new LoginPresenter(eventBus, service, new LoginWidget());
		container.clear();
		loginPresenter.go(container); 
	}
	
	private void displayContent(final String username) {
		container.clear(); 
		service.getCourses(new AsyncCallback<Course[]>() {

			@Override
			public void onFailure(Throwable caught) {
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
				headerPresenter = new HeaderPresenter(eventBus, service, new HeaderWidget(username));
				headerPresenter.setCourses(courses); 
				 
				headerPresenter.go(container); 
				selectCourse(courses.get(0).id); 
				/* add the content container */
				container.add(content); 
				/* initialize history entries */
				if ("".equals(History.getToken())) {
					History.newItem(courses.get(0).id);
					//History.newItem("assignments");
				} else {
					History.fireCurrentHistoryState(); 
				}
			}			
		}); 		
	}
	
	public void onValueChange(ValueChangeEvent<String> event) {
		String token = event.getValue();
		if (token != null) {
			if ("".equals(token)) {
				token = courses.get(0).id;
				History.newItem(token); 
				return; 
			}
			
			if (coursesTags.contains(token)) {
				if (mainPresenter != null) {
					mainPresenter.clearEventHandlers(); 
				}
				mainPresenter = new AssignmentPresenter(eventBus, service, idToCourse.get(token).id, new AssignmentWidget());
				headerPresenter.selectCourse(idToCourse.get(token).id); 
			} else {
				Window.alert("State " + token + " not implemented");
			}
			
			if (mainPresenter != null) {
				content.clear();
				mainPresenter.go(content); 
			}
		}
	}
	
	private void bindHistory() {
		History.addValueChangeHandler(this); 
	}
}
