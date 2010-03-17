package ro.pub.cs.vmchecker.client.ui;

import ro.pub.cs.vmchecker.client.presenter.AssignmentBoardPresenter;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class ResultsWidget extends Composite 
	implements AssignmentBoardPresenter.ResultsWidget {

	private static ResultsWidgetUiBinder uiBinder = GWT
			.create(ResultsWidgetUiBinder.class);

	interface ResultsWidgetUiBinder extends UiBinder<Widget, ResultsWidget> {
	}

	public ResultsWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	@UiField
	Label container;

	@Override
	public HasText getResultContainer() {
		return container; 
	} 
	

}
