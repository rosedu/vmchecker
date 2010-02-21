package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class StatementWidget extends Composite {

	private static StatementWidgetUiBinder uiBinder = GWT
			.create(StatementWidgetUiBinder.class);

	interface StatementWidgetUiBinder extends UiBinder<Widget, StatementWidget> {
	}

	public StatementWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

}
