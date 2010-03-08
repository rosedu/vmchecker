package ro.pub.cs.vmchecker.client.presenter;

import java.util.ArrayList;
import java.util.HashMap;

import ro.pub.cs.vmchecker.client.event.CourseSelectedEvent;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent;
import ro.pub.cs.vmchecker.client.event.StatusChangedEventHandler;
import ro.pub.cs.vmchecker.client.model.Course;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.event.dom.client.HasChangeHandlers;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.Widget;

public class HeaderPresenter implements Presenter {

	private HandlerManager eventBus;
	private HeaderWidget widget; 
	private HasWidgets container; 
	
	
	private HashMap<String, Integer> idToIndex = new HashMap<String, Integer>();
	private ArrayList<String> coursesIds = new ArrayList<String>(); 
	private String statusMessage = ""; 
	
	public interface HeaderWidget {
		HasText getStatusLabel();
		void setStatusLabelVisible(boolean visible); 
		HasChangeHandlers getCoursesList(); 
		void addCourse(String name, String id);
		void clearCourses();
		void selectCourse(int courseIndex);
		int getSelectedCourseIndex(); 
	}
	
	public HeaderPresenter(HandlerManager eventBus, HeaderWidget widget) {
		this.eventBus = eventBus; 
		bindWidget(widget);
		listenStatusChange(); 
	}
	
	private void listenStatusChange() {
		this.eventBus.addHandler(StatusChangedEvent.TYPE, new StatusChangedEventHandler() {

			public void onChange(StatusChangedEvent event) {
				if (event.getType() == StatusChangedEvent.StatusType.RESET) {
					widget.setStatusLabelVisible(false); 
				} else {
					widget.getStatusLabel().setText(event.getText());
					widget.setStatusLabelVisible(true); 
				}
			}
			
		}); 
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
