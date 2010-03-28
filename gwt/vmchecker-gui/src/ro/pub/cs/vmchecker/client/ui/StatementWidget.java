package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.Widget;

import ro.pub.cs.vmchecker.client.presenter.AssignmentBoardPresenter;

public class StatementWidget extends Composite 
	implements AssignmentBoardPresenter.StatementWidget {

	private static StatementWidgetUiBinder uiBinder = GWT
			.create(StatementWidgetUiBinder.class);

	interface StatementWidgetUiBinder extends UiBinder<Widget, StatementWidget> {
	}

	@UiField
	FlowPanel container; 
	
	@UiField
	Anchor statementAnchor; 
	
	public StatementWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		statementAnchor.setTarget("_new"); 
	}

	@Override
	public void setStatementHref(String statementHref) {
		statementAnchor.setHref(statementHref); 
	}

}
