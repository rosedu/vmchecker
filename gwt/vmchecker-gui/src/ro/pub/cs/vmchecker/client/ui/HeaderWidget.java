package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.HasChangeHandlers;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.Widget;

import ro.pub.cs.vmchecker.client.presenter.HeaderPresenter; 

public class HeaderWidget extends Composite 
	implements HeaderPresenter.HeaderWidget {

	interface HeaderUiBinder extends UiBinder<Widget, HeaderWidget> {}
	private static HeaderUiBinder uiBinder = GWT.create(HeaderUiBinder.class);

	private static String[] courses = {"Sisteme de Operare", "Compilatoare", "Sisteme de Operare II"};
	
	@UiField 
	ListBox coursesList; 
	
	@UiField 
	Label statusLabel; 
	
	public HeaderWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		for (String course : courses) {
			coursesList.addItem(course); 
		}
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
	
}
