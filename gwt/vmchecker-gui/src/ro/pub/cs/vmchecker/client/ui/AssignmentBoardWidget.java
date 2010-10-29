package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;

import ro.pub.cs.vmchecker.client.i18n.AssignmentBoardConstants;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.logical.shared.HasSelectionHandlers;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.SimplePanel;
import com.google.gwt.user.client.ui.TabBar;
import com.google.gwt.user.client.ui.Widget;
import ro.pub.cs.vmchecker.client.presenter.AssignmentBoardPresenter;
import com.google.gwt.user.client.Element;

public class AssignmentBoardWidget extends Composite
	implements AssignmentBoardPresenter.Widget {

	private static AssignmentBoardUiBinder uiBinder = GWT
			.create(AssignmentBoardUiBinder.class);

	private static AssignmentBoardConstants constants = GWT
			.create(AssignmentBoardConstants.class);

	interface AssignmentBoardUiBinder extends UiBinder<Widget, AssignmentBoardWidget> {
	}

	@UiField
	TabBar menu;

	@UiField
	SimplePanel viewStack;

	@UiField
	Label title;

	@UiField
	Label deadlineText;

	@UiField
	Label deadlineDate;

	public AssignmentBoardWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		deadlineText.setText(constants.deadlineText());
		for (String entry : viewTitles) {
			menu.addTab(constants.getString(entry));
		}
		menu.selectTab(defaultView);
		/* HACK: align tab menu to the right */
		Element menuRest = (Element)menu.getElement().getFirstChildElement().getFirstChildElement().getLastChild();
		menuRest.removeAttribute("width");
		//GWT.log(menuRest.getString(), null);
	}

	@Override
	public HasText getDeadlineLabel() {
		return deadlineDate;
	}

	@Override
	public HasText getTitleLabel() {
		return title;
	}

	@Override
	public HasWidgets getViewStack() {
		return viewStack;
	}

	@Override
	public void displayView(com.google.gwt.user.client.ui.Widget view) {
		viewStack.clear();
		viewStack.add(view);
	}

	@Override
	public HasSelectionHandlers<Integer> getMenu() {
		return menu;
	}

	@Override
	public void setSelectedTab(int tabIndex) {
		menu.selectTab(tabIndex);
	}

}
