package ro.pub.cs.vmchecker.client.ui;

import ro.pub.cs.vmchecker.client.i18n.VmcheckerConstants;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.Event.NativePreviewEvent;
import com.google.gwt.core.client.Scheduler;
import com.google.gwt.dom.client.Style;
import com.google.gwt.dom.client.Style.Overflow;
import com.google.gwt.dom.client.Document;

/**
 * Wrapper over the classic PopupPanel
 * Adds a close button and a scrollable content panel
 * @author claudiugh
 * Implement proper scrolling support and make sure
 * the body doesn't scroll when used.
 * @author calin.iorgulescu
 *
 */
public class VmcheckerPopup extends PopupPanel {

	private static final String containerStyle = "popupContainer";
	private static final String contentStyle = "popupContentPanel";

	private static VmcheckerConstants constants = GWT
			.create(VmcheckerConstants.class);
	private FlowPanel detailsPopupContainer = new FlowPanel();
	private ScrollPanel detailsPopupContent = new ScrollPanel();
	private Anchor popupCloseButton = new Anchor();

	public VmcheckerPopup() {
		super(true);
		setup();
	}

	private void setup() {
		hide();
		popupCloseButton.setText(constants.popupCloseButton());
		setWidth("" + (3 * Window.getClientWidth() / 4) + "px");
		setHeight("" + (Window.getClientHeight() - 200) + "px");
		setGlassEnabled(true);
		detailsPopupContainer.add(popupCloseButton);
		detailsPopupContainer.add(detailsPopupContent);
		detailsPopupContent.setWidth("" + ((3 * Window.getClientWidth() / 4) - 10) + "px");
		detailsPopupContent.setHeight("" + (Window.getClientHeight() - 250) + "px");
		add(detailsPopupContainer);
		detailsPopupContainer.setStyleName(containerStyle);
		detailsPopupContent.setStyleName(contentStyle);
		popupCloseButton.setStyleName("");
		popupCloseButton.addClickHandler(new ClickHandler() {
			@Override
			public void onClick(ClickEvent event) {
				hide();
			}
		});

	}

	public void showContent(String htmlContent) {
		detailsPopupContent.clear();
		detailsPopupContent.add(new HTML(htmlContent));
		center();
		show();
		Document.get().getBody().getStyle().setOverflow(Style.Overflow.HIDDEN);
	}

	@Override
	protected void onPreviewNativeEvent(NativePreviewEvent event) {
		super.onPreviewNativeEvent(event);
		if (!isShowing()) {
			return;
		}

		switch (event.getTypeInt()) {
			case Event.ONKEYDOWN:
				if (event.getNativeEvent().getKeyCode() == KeyCodes.KEY_ESCAPE) {
					hide();
				}
				// XXX: It seems that on Chrome or Safari focusing the scrollpanel doesn't work.
				// There's probably a better way to do this, but for now, it'll do.
				if (event.getNativeEvent().getKeyCode() == KeyCodes.KEY_DOWN) {
					int scrollIncrement = (detailsPopupContent.getMaximumVerticalScrollPosition() - 
						detailsPopupContent.getMinimumVerticalScrollPosition()) / 200;
					if (detailsPopupContent.getVerticalScrollPosition() <
							detailsPopupContent.getMaximumVerticalScrollPosition()) {
						detailsPopupContent.setVerticalScrollPosition(
							detailsPopupContent.getVerticalScrollPosition() + scrollIncrement);
					}
				}

				if (event.getNativeEvent().getKeyCode() == KeyCodes.KEY_UP) {
					int scrollIncrement = (detailsPopupContent.getMaximumVerticalScrollPosition() - 
						detailsPopupContent.getMinimumVerticalScrollPosition()) / 200;
					if (detailsPopupContent.getVerticalScrollPosition() >
							detailsPopupContent.getMinimumVerticalScrollPosition()) {
						detailsPopupContent.setVerticalScrollPosition(
							detailsPopupContent.getVerticalScrollPosition() - scrollIncrement);
					}
				}

				if (event.getNativeEvent().getKeyCode() == KeyCodes.KEY_PAGEDOWN) {
					int scrollIncrement = (detailsPopupContent.getMaximumVerticalScrollPosition() - 
						detailsPopupContent.getMinimumVerticalScrollPosition()) / 20;
					if (detailsPopupContent.getVerticalScrollPosition() <
							detailsPopupContent.getMaximumVerticalScrollPosition()) {
						detailsPopupContent.setVerticalScrollPosition(
							detailsPopupContent.getVerticalScrollPosition() + scrollIncrement);
					}
				}

				if (event.getNativeEvent().getKeyCode() == KeyCodes.KEY_PAGEUP) {
					int scrollIncrement = (detailsPopupContent.getMaximumVerticalScrollPosition() - 
						detailsPopupContent.getMinimumVerticalScrollPosition()) / 20;
					if (detailsPopupContent.getVerticalScrollPosition() >
							detailsPopupContent.getMinimumVerticalScrollPosition()) {
						detailsPopupContent.setVerticalScrollPosition(
							detailsPopupContent.getVerticalScrollPosition() - scrollIncrement);
					}
				}

				if (event.getNativeEvent().getKeyCode() == KeyCodes.KEY_END) {
					detailsPopupContent.scrollToBottom();
				}

				if (event.getNativeEvent().getKeyCode() == KeyCodes.KEY_HOME) {
					detailsPopupContent.scrollToTop();
				}

				event.cancel();
				break;
		}
	}

	@Override
	protected void onUnload() {
		super.onUnload();
		Document.get().getBody().getStyle().clearOverflow();
	}

}
