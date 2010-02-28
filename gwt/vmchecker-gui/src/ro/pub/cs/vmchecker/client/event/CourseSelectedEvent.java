package ro.pub.cs.vmchecker.client.event;

import com.google.gwt.event.shared.GwtEvent;

public class CourseSelectedEvent extends GwtEvent<CourseSelectedEventHandler> {

	public static final GwtEvent.Type<CourseSelectedEventHandler> TYPE = new GwtEvent.Type<CourseSelectedEventHandler>(); 
	
	private String courseId; 
	
	public CourseSelectedEvent(String courseId) {
		this.courseId = courseId; 
	}
	
	public String getCourseId() {
		return courseId; 
	}
	
	@Override
	protected void dispatch(CourseSelectedEventHandler handler) {
		handler.onSelect(this); 
	}

	@Override
	public GwtEvent.Type<CourseSelectedEventHandler> getAssociatedType() {
		return TYPE; 
	}

}
