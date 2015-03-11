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

import ro.pub.cs.vmchecker.client.i18n.ServerTimeConstants;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent.StatusType;
import ro.pub.cs.vmchecker.client.presenter.ServerTimePresenter;

public class ServerTimeWidget extends Composite
	implements ServerTimePresenter.Widget {

	interface ServerTimeUiBinder extends UiBinder<Widget, ServerTimeWidget> {}
	private static ServerTimeUiBinder uiBinder = GWT.create(ServerTimeUiBinder.class);

	@UiField
	Label serverTimeMsg;

	@UiField
	Label serverTime;

	@UiField
	Label browserTimeOffsetMsg;

	@UiField
	Label browserTimeOffset;

	private static ServerTimeConstants constants = GWT
			.create(ServerTimeConstants.class);

	public ServerTimeWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		serverTimeMsg.setText(constants.serverTimeMsg());
	}

	@Override
	public HasText getServerTime() {
		return serverTime;
	}

	@Override
	public HasText getBrowserTimeOffset() {
		return browserTimeOffset;
	}

	@Override
	public HasText getBrowserTimeOffsetMsg() {
		return browserTimeOffsetMsg;
	}
}
