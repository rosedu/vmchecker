package ro.pub.cs.vmchecker.client.presenter;

import java.util.ArrayList;
import java.util.HashMap;

import ro.pub.cs.vmchecker.client.event.AuthenticationEvent;
import ro.pub.cs.vmchecker.client.event.CourseSelectedEvent;
import ro.pub.cs.vmchecker.client.event.ErrorDisplayEvent;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent;
import ro.pub.cs.vmchecker.client.event.StatusChangedEventHandler;
import ro.pub.cs.vmchecker.client.model.Course;
import ro.pub.cs.vmchecker.client.service.HTTPService;

import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.HasChangeHandlers;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.Widget;

import com.google.gwt.core.client.GWT;
public class StatusPresenter implements Presenter {

	private EventBus eventBus;
	private HTTPService service; 
	private StatusWidget widget; 
	private HasWidgets container; 
	
	
	private String statusDetails = ""; 
	
	public interface StatusWidget {
		HasText getStatusLabel();
		HasClickHandlers getStatusDetailsButton();
		void setStatusVisible(boolean visible);
		void setStatusDetailsButtonVisible(boolean visible);
		void showStatusDetails(String details); 
		void setStatusType(StatusChangedEvent.StatusType type);
	}
	
	public StatusPresenter(EventBus eventBus, HTTPService service, StatusWidget widget) {
		this.eventBus = eventBus; 
		this.service = service; 
		this.widget = widget; 
		listenStatusChange();
		listenStatusDetails(); 
	}
	
	private void listenStatusDetails() {
		widget.getStatusDetailsButton().addClickHandler(new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				widget.showStatusDetails(statusDetails); 
			}
			
		}); 
	}
	
	private void displayError(ErrorDisplayEvent event) {
		widget.setStatusType(event.getType());
		widget.getStatusLabel().setText(event.getText());
		statusDetails = event.getDetails(); 
		widget.setStatusDetailsButtonVisible(true); 
		widget.setStatusVisible(true); 		
	}
	
	private void listenStatusChange() {
		this.eventBus.addHandler(StatusChangedEvent.TYPE, new StatusChangedEventHandler() {
			public void onChange(StatusChangedEvent event) {
				if (event.getType() == StatusChangedEvent.StatusType.RESET) {
					widget.setStatusVisible(false); 
				} else if (event instanceof ErrorDisplayEvent) {
					GWT.log("ErrorDisplayEvent received.", null);
					displayError((ErrorDisplayEvent)event); 
				} else {
					widget.getStatusLabel().setText(event.getText());
					widget.setStatusType(event.getType()); 
					widget.setStatusDetailsButtonVisible(false); 
					widget.setStatusVisible(true);
				}
			}
		}); 
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
