package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.SimplePanel;
import com.google.gwt.user.client.ui.Widget;
import ro.pub.cs.vmchecker.client.presenter.AssignmentPresenter;

public class AssignmentWidget extends Composite 
 	implements AssignmentPresenter.AssignmentWidget {

	private static AssignmentWidgetUiBinder uiBinder = GWT
			.create(AssignmentWidgetUiBinder.class);

	interface AssignmentWidgetUiBinder extends
			UiBinder<Widget, AssignmentWidget> {
	}

	@UiField
	SimplePanel menuPanel; 
	
	@UiField
	SimplePanel boardPanel; 
	
	@UiField
	Anchor viewStatsButton; 
	
	public AssignmentWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	@Override
	public HasWidgets getBoardPanel() {
		return boardPanel; 
	}

	@Override
	public HasWidgets getMenuPanel() {
		return menuPanel; 
	}

	@Override
	public HasClickHandlers getViewStatsButton() {
		return viewStatsButton; 
	}

}
