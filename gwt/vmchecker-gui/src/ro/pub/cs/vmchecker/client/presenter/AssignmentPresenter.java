package ro.pub.cs.vmchecker.client.presenter;

import ro.pub.cs.vmchecker.client.event.AssignmentSelectedEvent;
import ro.pub.cs.vmchecker.client.event.ErrorDisplayEvent;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent;
import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.service.HTTPService;
import ro.pub.cs.vmchecker.client.ui.AssignmentBoardWidget;
import ro.pub.cs.vmchecker.client.ui.NumberedMenu;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.Widget;

public class AssignmentPresenter implements Presenter {

	private HandlerManager eventBus;
	private HTTPService service; 
	private AssignmentWidget widget; 
	
	private Assignment[] assignments; 
	private String courseId; 
	
	private MenuPresenter menuPresenter; 
	private AssignmentBoardPresenter boardPresenter; 
	
	public interface AssignmentWidget {
		HasWidgets getMenuPanel();
		HasWidgets getBoardPanel(); 
	}
	
	public AssignmentPresenter(HandlerManager eventBus, HTTPService service, String courseId, AssignmentWidget widget) {
		this.eventBus = eventBus;
		this.service = service; 
		this.courseId = courseId;		
		this.widget = widget;
	}
	
	private void bindWidget(AssignmentWidget widget) {
		menuPresenter.getWidget().addClickHandler(new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				int assignmentIndex = menuPresenter.getWidget().getSelectedIndex(); 
				fireAssignmentSelected(assignmentIndex); 
			}
		});
	}
	
	private void fireAssignmentSelected(int assignmentIndex) {
		eventBus.fireEvent(new AssignmentSelectedEvent(assignments[assignmentIndex].id, 
				assignments[assignmentIndex])); 		
	}
	
	@Override
	public void go(final HasWidgets container) {
		eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION, "Incarca teme...")); 
		service.getAssignments(courseId, new AsyncCallback<Assignment[]>(){

			public void onFailure(Throwable caught) {
				GWT.log("[AssignmentPresenter]", caught); 
				eventBus.fireEvent(new ErrorDisplayEvent("[Service error]" + caught.toString(), caught.getMessage())); 
			}

			public void onSuccess(Assignment[] result) {				
				/* extract titles */
				assignments = result; 
				String[] titles = new String[assignments.length]; 
				for (int i = 0; i < assignments.length; i++) {
					titles[i] = assignments[i].title; 
				}
				menuPresenter = new MenuPresenter(eventBus, new NumberedMenu(titles)); 
				boardPresenter = new AssignmentBoardPresenter(eventBus, service, courseId, new AssignmentBoardWidget());
				bindWidget(widget);
				
				widget.getMenuPanel().clear(); 
				menuPresenter.go(widget.getMenuPanel()); 
				widget.getBoardPanel().clear(); 
				boardPresenter.go(widget.getBoardPanel()); 
				/* init */
				menuPresenter.getWidget().setSelectedIndex(0);
				//fireAssignmentSelected(0); 
				boardPresenter.assignmentSelected(assignments[0]); 
				container.add((Widget)widget);
				
				eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.RESET, null)); 
			}
			
		}); 
		
	}

	@Override
	public void clearEventHandlers() {
		menuPresenter.clearEventHandlers(); 
		boardPresenter.clearEventHandlers(); 
	}

}
