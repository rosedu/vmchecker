package ro.pub.cs.vmchecker.client.presenter;

import ro.pub.cs.vmchecker.client.event.AssignmentSelectedEvent;
import ro.pub.cs.vmchecker.client.event.AssignmentSelectedEventHandler;
import ro.pub.cs.vmchecker.client.ui.ResultsWidget;
import ro.pub.cs.vmchecker.client.ui.StatementWidget;
import ro.pub.cs.vmchecker.client.ui.UploadWidget;

import com.google.gwt.event.logical.shared.HasSelectionHandlers;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;
import com.google.gwt.event.shared.HandlerManager;
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
	
	public AssignmentBoardPresenter(HandlerManager eventBus, AssignmentBoardPresenter.Widget widget) {
		this.eventBus = eventBus;
		listenAssignmentSelect(); 
		bindWidget(widget); 
	}
	
	public void listenAssignmentSelect() {
		eventBus.addHandler(AssignmentSelectedEvent.TYPE, new AssignmentSelectedEventHandler() {

			public void onSelect(AssignmentSelectedEvent event) {
				container.clear(); 
				widget.getTitleLabel().setText(event.data.title); 
				widget.getDeadlineLabel().setText(event.data.deadline);
				setVisibleView(Widget.defaultView);
				widget.setSelectedTab(Widget.defaultView); 
				container.add((com.google.gwt.user.client.ui.Widget)widget); 
			}			
		}); 
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
	}

}
