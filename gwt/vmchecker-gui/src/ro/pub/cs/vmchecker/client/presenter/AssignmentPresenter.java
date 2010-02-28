package ro.pub.cs.vmchecker.client.presenter;

import java.util.ArrayList;

import ro.pub.cs.vmchecker.client.event.AssignmentSelectedEvent;
import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.ui.AssignmentBoard;
import ro.pub.cs.vmchecker.client.ui.NumberedMenu;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.Widget;

public class AssignmentPresenter implements Presenter {

	private HandlerManager eventBus; 
	private AssignmentWidget widget; 
	
	private ArrayList<Assignment> assignments; 
	private String courseId; 
	
	private MenuPresenter menuPresenter; 
	private AssignmentBoardPresenter boardPresenter; 
	
	public interface AssignmentWidget {
		HasWidgets getMenuPanel();
		HasWidgets getBoardPanel(); 
	}
	
	public AssignmentPresenter(HandlerManager eventBus, String courseId, AssignmentWidget widget) {
		this.eventBus = eventBus;
		this.courseId = courseId; 
		assignments = new ArrayList<Assignment>(); 
		assignments.add(new Assignment("tema1-lin", "Mini shell", "2001-10-9")); 
		assignments.add(new Assignment("tema2-lin", "Shared hash table", "2008-12-9"));
		assignments.add(new Assignment("tema3-win", "Monitor generic", "2010-01-04"));
		String[] titles = new String[assignments.size()]; 
		for (int i = 0; i < assignments.size(); i++) {
			titles[i] = assignments.get(i).title; 
		}
		menuPresenter = new MenuPresenter(eventBus, new NumberedMenu(titles), titles); 
		boardPresenter = new AssignmentBoardPresenter(eventBus, new AssignmentBoard());
		bindWidget(widget); 
	}
	
	private void bindWidget(AssignmentWidget widget) {
		this.widget = widget;
		menuPresenter.getWidget().addClickHandler(new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				int assignmentIndex = menuPresenter.getWidget().getSelectedIndex(); 
				GWT.log("Assignment number " +  assignmentIndex + " was selected", null);
				fireAssignmentSelected(assignmentIndex); 
			}
		});
	}
	
	private void fireAssignmentSelected(int assignmentIndex) {
		GWT.log("Event fired", null); 
		eventBus.fireEvent(new AssignmentSelectedEvent(assignments.get(assignmentIndex).id, 
				assignments.get(assignmentIndex))); 		
	}
	
	@Override
	public void go(HasWidgets container) {
		widget.getMenuPanel().clear(); 
		menuPresenter.go(widget.getMenuPanel()); 
		widget.getBoardPanel().clear(); 
		boardPresenter.go(widget.getBoardPanel()); 
		/* init */
		menuPresenter.getWidget().setSelectedIndex(0);
		
		//fireAssignmentSelected(0); 
		boardPresenter.assignmentSelected(assignments.get(0)); 
		container.add((Widget)widget);
	}

	@Override
	public void clearEventHandlers() {
		menuPresenter.clearEventHandlers(); 
		boardPresenter.clearEventHandlers(); 
	}

}
