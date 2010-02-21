package ro.pub.cs.vmchecker.client.presenter;

import java.util.ArrayList;
import java.util.HashMap;

import ro.pub.cs.vmchecker.client.model.Course;

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
	
	public interface HeaderWidget {
		HasText getStatusLabel();
		HasChangeHandlers getCoursesList(); 
		void addCourse(String name, String id);
		void clearCourses();
		void selectCourse(int courseIndex); 
	}
	
	public HeaderPresenter(HandlerManager eventBus, HeaderWidget widget) {
		this.eventBus = eventBus; 
		bindWidget(widget); 
	}
	
	public void setCourses(ArrayList<Course> courses) {
		widget.clearCourses();
		
		for (int i = 0; i < courses.size(); i++) {
			Course course = courses.get(i); 
			widget.addCourse(course.title, course.id);
			idToIndex.put(course.id, i); 
		}
	}
	
	private void bindWidget(HeaderWidget widget) {
		this.widget = widget; 
		/* listen to events from display */
	}
	
	public void selectCourse(String courseId) {
		widget.selectCourse(idToIndex.get(courseId)); 
	}
	
	public Widget getWidget() {
		return (Widget) widget; 
	}

	@Override
	public void go(HasWidgets container) {
		this.container = container; 
		this.container.add((Widget)widget);  
	}
	
	
}
