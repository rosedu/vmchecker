package ro.pub.cs.vmchecker.client.event;

import ro.pub.cs.vmchecker.client.model.Assignment;

import com.google.gwt.event.shared.GwtEvent;

public class AssignmentSelectedEvent extends GwtEvent<AssignmentSelectedEventHandler> {

	public static final GwtEvent.Type<AssignmentSelectedEventHandler> TYPE 
		= new GwtEvent.Type<AssignmentSelectedEventHandler>(); 
	
	private String assignmentId; 
	public Assignment data; 
	
	public AssignmentSelectedEvent(String assignmentId, Assignment assignment) {
		this.assignmentId = assignmentId;
		this.data = assignment; 
	}
	
	public String getAssignmentId() {
		return assignmentId; 
	}
	
	@Override
	protected void dispatch(AssignmentSelectedEventHandler handler) {
		handler.onSelect(this); 
	}

	@Override
	public GwtEvent.Type<AssignmentSelectedEventHandler> getAssociatedType() {
		return TYPE;
	}

}
