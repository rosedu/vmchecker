package ro.pub.cs.vmchecker.client.presenter;

import java.util.ArrayList;
import java.util.HashMap;

import ro.pub.cs.vmchecker.client.event.AuthenticationEvent;
import ro.pub.cs.vmchecker.client.event.CourseSelectedEvent;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent;
import ro.pub.cs.vmchecker.client.event.StatusChangedEventHandler;
import ro.pub.cs.vmchecker.client.model.Course;
import ro.pub.cs.vmchecker.client.service.HTTPService;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.HasChangeHandlers;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.resources.client.CssResource;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.Widget;

public class HeaderPresenter implements Presenter {

	private HandlerManager eventBus;
	private HTTPService service; 
	private HeaderWidget widget; 
	private HasWidgets container; 
	
	
	private HashMap<String, Integer> idToIndex = new HashMap<String, Integer>();
	private ArrayList<String> coursesIds = new ArrayList<String>(); 
	private String statusMessage = ""; 
	
	public interface HeaderWidget {
		HasText getStatusLabel();
		HasText getUsernameLabel(); 
		void setStatusLabelVisible(boolean visible);
		HasClickHandlers getLogoutButton(); 
		HasChangeHandlers getCoursesList(); 
		void addCourse(String name, String id);
		void clearCourses();
		void selectCourse(int courseIndex);
		int getSelectedCourseIndex();
		void setStatusType(StatusChangedEvent.StatusType type);
	}
	
	public HeaderPresenter(HandlerManager eventBus, HTTPService service, HeaderWidget widget) {
		this.eventBus = eventBus; 
		this.service = service; 
		bindWidget(widget);
		listenStatusChange(); 
	}
	
	public void setCourses(ArrayList<Course> courses) {
		widget.clearCourses();
		
		for (int i = 0; i < courses.size(); i++) {
			Course course = courses.get(i); 
			widget.addCourse(course.title, course.id);
			idToIndex.put(course.id, i);
			coursesIds.add(course.id); 
		}
	}
	
	private void bindWidget(HeaderWidget widget) {
		this.widget = widget; 
		/* listen to events from display */
		listenCourseChange(); 
		listenLogoutRequest(); 
	}
	
	private void performLogout() {
		service.sendLogoutRequest(new AsyncCallback<Boolean>() {

			@Override
			public void onFailure(Throwable caught) {
				Window.alert(caught.getMessage()); 
			}

			@Override
			public void onSuccess(Boolean result) {
				/* force a check that will eventually fail and will display the login screen */
				eventBus.fireEvent(new AuthenticationEvent(AuthenticationEvent.EventType.FORCE_CHECK)); 
			}
			
		}); 
	}
	
	private void listenLogoutRequest() {
		widget.getLogoutButton().addClickHandler(new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				performLogout(); 
			}
			
		}); 
	}
	
	private void listenStatusChange() {
		this.eventBus.addHandler(StatusChangedEvent.TYPE, new StatusChangedEventHandler() {
			public void onChange(StatusChangedEvent event) {
				if (event.getType() == StatusChangedEvent.StatusType.RESET) {
					widget.setStatusLabelVisible(false); 
				} else {
					widget.getStatusLabel().setText(event.getText());
					widget.setStatusType(event.getType()); 
					widget.setStatusLabelVisible(true); 
				}
			}
		}); 
	}
	
	private void listenCourseChange() {
		widget.getCoursesList().addChangeHandler(new ChangeHandler() {
			public void onChange(ChangeEvent event) {
				String newCourseId = coursesIds.get(widget.getSelectedCourseIndex()); 
				CourseSelectedEvent courseEvent = new CourseSelectedEvent(newCourseId);
				eventBus.fireEvent(courseEvent); 
			}			
		}); 
	}
	
	public void selectCourse(String courseId) {
		if (widget.getSelectedCourseIndex() != idToIndex.get(courseId)) {
			widget.selectCourse(idToIndex.get(courseId)); 
		}
	}
	
	public Widget getWidget() {
		return (Widget) widget; 
	}

	@Override
	public void go(HasWidgets container) {
		this.container = container; 
		this.container.add((Widget)widget);  
	}

	@Override
	public void clearEventHandlers() {
		/* nothing */
	}
	
	
}
