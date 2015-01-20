package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.HasChangeHandlers;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.resources.client.CssResource;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.Widget;

import ro.pub.cs.vmchecker.client.i18n.VmcheckerConstants;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent.StatusType;
import ro.pub.cs.vmchecker.client.presenter.HeaderPresenter;
import ro.pub.cs.vmchecker.client.model.User;

public class HeaderWidget extends Composite
	implements HeaderPresenter.HeaderWidget {

	interface HeaderUiBinder extends UiBinder<Widget, HeaderWidget> {}
	private static HeaderUiBinder uiBinder = GWT.create(HeaderUiBinder.class);

	@UiField
	Label courseSelection;

	@UiField
	ListBox coursesList;

	@UiField
	Label usernameLabel;

	@UiField
	Anchor logoutButton;

	private static VmcheckerConstants constants = GWT
			.create(VmcheckerConstants.class);

	public HeaderWidget(User user) {
		initWidget(uiBinder.createAndBindUi(this));
		courseSelection.setText(constants.courseSelection());
		logoutButton.setText(constants.logoutButton());
		usernameLabel.setText(user.name + " (" + user.id + ")");
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
	public HasText getUsernameLabel() {
		return usernameLabel;
	}

	@Override
	public HasClickHandlers getLogoutButton() {
		return logoutButton;
	}

}
