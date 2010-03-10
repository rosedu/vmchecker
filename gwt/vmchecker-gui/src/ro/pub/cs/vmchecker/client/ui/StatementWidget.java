package ro.pub.cs.vmchecker.client.ui;

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

import ro.pub.cs.vmchecker.client.presenter.AssignmentBoardPresenter;

public class StatementWidget extends Composite 
	implements AssignmentBoardPresenter.StatementWidget {

	private static StatementWidgetUiBinder uiBinder = GWT
			.create(StatementWidgetUiBinder.class);

	interface StatementWidgetUiBinder extends UiBinder<Widget, StatementWidget> {
	}

	@UiField
	Label container; 
	
	public StatementWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	@Override
	public HasText getStatementContainer() {
		return container; 
	}

}
