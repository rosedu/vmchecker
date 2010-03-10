package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.HasChangeHandlers;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.resources.client.CssResource;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.Widget;

import ro.pub.cs.vmchecker.client.event.StatusChangedEvent.StatusType;
import ro.pub.cs.vmchecker.client.presenter.HeaderPresenter; 

public class HeaderWidget extends Composite 
	implements HeaderPresenter.HeaderWidget {

	interface HeaderUiBinder extends UiBinder<Widget, HeaderWidget> {}
	private static HeaderUiBinder uiBinder = GWT.create(HeaderUiBinder.class);

	interface HeaderStyle extends CssResource {
		String info(); 
		String error(); 
		String success(); 
		String action(); 
	}
	
	@UiField 
	ListBox coursesList; 
	
	@UiField 
	Label statusLabel; 
	
	@UiField
	Label usernameLabel; 
	
	@UiField 
	HeaderStyle style; 
	
	@UiField
	Anchor logoutButton; 
	
	private String[] statusStyles = new String[4]; 
	
	public HeaderWidget(String username) {
		initWidget(uiBinder.createAndBindUi(this));
		usernameLabel.setText(username); 
		statusStyles[0] = style.action();  
		statusStyles[1] = style.error();  
		statusStyles[2] = style.success();   
		statusStyles[3] = style.info();   
	}

	@Override
	public HasText getStatusLabel() {
		return statusLabel; 
	}

	@Override
	public void addCourse(String name, String id) {
		coursesList.addItem(name, id); 
	}

	@Override
	public void clearCourses() {
		coursesList.clear(); 
	}

	@Override
	public void selectCourse(int courseIndex) {
		coursesList.setSelectedIndex(courseIndex); 
	}

	@Override
	public HasChangeHandlers getCoursesList() {
		return coursesList; 
	}

	@Override
	public int getSelectedCourseIndex() {
		return coursesList.getSelectedIndex(); 
	}

	@Override
	public void setStatusLabelVisible(boolean visible) {
		statusLabel.setVisible(visible); 
	}

	@Override
	public void setStatusType(StatusType type) {
		for (int i = 0; i < statusStyles.length; i++) {
			statusLabel.removeStyleName(statusStyles[i]); 
		}
		switch (type) {
		case ACTION:
			statusLabel.addStyleName(style.action()); 
			break; 
		case ERROR:
			statusLabel.addStyleName(style.error()); 
			break; 
		case SUCCESS:
			statusLabel.addStyleName(style.success()); 
			break; 
		case INFO:
			statusLabel.addStyleName(style.info()); 
			break; 
		}
	}

	@Override
	public HasText getUsernameLabel() {
		return usernameLabel; 
	}

	@Override
	public HasClickHandlers getLogoutButton() {
		return logoutButton; 
	}

}
