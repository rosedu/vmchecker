package ro.pub.cs.vmchecker.client.presenter;

import ro.pub.cs.vmchecker.client.event.AssignmentSelectedEvent;
import ro.pub.cs.vmchecker.client.event.AssignmentSelectedEventHandler;
import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.ui.ResultsWidget;
import ro.pub.cs.vmchecker.client.ui.StatementWidget;
import ro.pub.cs.vmchecker.client.ui.UploadWidget;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.logical.shared.HasSelectionHandlers;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.event.shared.GwtEvent.Type;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HasWidgets;

public class AssignmentBoardPresenter implements Presenter {

	public interface Widget {
		public static enum View {
			UPLOAD, STATEMENT, RESULTS
		}; 
		
		public static final String[] viewTitles = {
			"Trimitere solutii", "Enunt", "Rezultate"
		}; 
		
		public static final int defaultView = 0; /* UPLOAD */
		
		HasText getTitleLabel();
		HasText getDeadlineLabel();
		HasSelectionHandlers<Integer> getMenu();
		void setSelectedTab(int tabIndex); 
		void displayView(com.google.gwt.user.client.ui.Widget view); 
	}
	
	private HandlerManager eventBus;
	private AssignmentBoardPresenter.Widget widget; 
	private HasWidgets container; 
	private HandlerRegistration assignmentSelectReg = null;
	
	public AssignmentBoardPresenter(HandlerManager eventBus, AssignmentBoardPresenter.Widget widget) {
		this.eventBus = eventBus;
		bindWidget(widget);
		listenAssignmentSelect(); 
	}
	
	public void listenAssignmentSelect() {
		assignmentSelectReg = eventBus.addHandler(AssignmentSelectedEvent.TYPE, new AssignmentSelectedEventHandler() {
			public void onSelect(AssignmentSelectedEvent event) {
				GWT.log("Assignment select event captured: " + widget.hashCode() + " " + container.hashCode(), null);
				assignmentSelected(event.data); 
			}			
		}); 
	}
	
	public void assignmentSelected(Assignment data) {
		widget.getTitleLabel().setText(data.title); 
		widget.getDeadlineLabel().setText(data.deadline);
		setVisibleView(Widget.defaultView);
		widget.setSelectedTab(Widget.defaultView); 
		((com.google.gwt.user.client.ui.Widget)widget).setVisible(true);
	}
	
	public void setVisibleView(int viewIndex) {
		Widget.View view = Widget.View.values()[viewIndex];
		switch (view) {
		case UPLOAD: 
			UploadWidget uploadWidget = new UploadWidget();
			widget.displayView(uploadWidget); 
			break; 
		case STATEMENT: 
			StatementWidget statementWidget = new StatementWidget(); 
			widget.displayView(statementWidget); 
			break; 			
		case RESULTS:
			ResultsWidget resultsWidget = new ResultsWidget(); 
			widget.displayView(resultsWidget); 
			break; 
		}
	}
	
	private void bindWidget(AssignmentBoardPresenter.Widget widget) {
		this.widget = widget;
		listenMenuSelection(); 
	}
	
	private void listenMenuSelection() {
		widget.getMenu().addSelectionHandler(new SelectionHandler<Integer> () {
			
			public void onSelection(SelectionEvent<Integer> event) {
				setVisibleView(event.getSelectedItem().intValue()); 
			}
		}); 
	}
	
	@Override
	public void go(HasWidgets container) {
		this.container = container;  
		container.clear(); 
		((com.google.gwt.user.client.ui.Widget)widget).setVisible(false); 
		container.add((com.google.gwt.user.client.ui.Widget)widget);
	}

	@Override
	public void clearEventHandlers() {
		assignmentSelectReg.removeHandler();
	}

}
