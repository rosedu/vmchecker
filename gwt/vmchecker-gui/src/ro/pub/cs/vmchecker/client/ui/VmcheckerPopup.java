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

/**
 * Wrapper over the classic PopupPanel
 * Adds a close button and a scrollable content panel
 * @author claudiugh
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
//		super(true, true);
		super(true, false);
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

/*
	private void focusContentPanel() {
		Scheduler.get().scheduleDeferred(new Scheduler.ScheduledCommand() {
			@Override
			public void execute() {
				detailsPopupContent.getElement().focus();
			}
		});
	}
*/

	public void showContent(String htmlContent) {
		detailsPopupContent.clear();
		detailsPopupContent.add(new HTML(htmlContent));
		center();
		show();
//		focusContentPanel();
	}

	@Override
	protected void onPreviewNativeEvent(NativePreviewEvent event) {
		super.onPreviewNativeEvent(event);
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

				if (event.getNativeEvent().getKeyCode() == KeyCodes.KEY_RIGHT) {
					int scrollIncrement = (detailsPopupContent.getMaximumHorizontalScrollPosition() - 
						detailsPopupContent.getMinimumHorizontalScrollPosition()) / 20;
					if (detailsPopupContent.getHorizontalScrollPosition() <
							detailsPopupContent.getMaximumHorizontalScrollPosition()) {
						detailsPopupContent.setHorizontalScrollPosition(
							detailsPopupContent.getHorizontalScrollPosition() + scrollIncrement);
					}
				}

				if (event.getNativeEvent().getKeyCode() == KeyCodes.KEY_LEFT) {
					int scrollIncrement = (detailsPopupContent.getMaximumHorizontalScrollPosition() - 
						detailsPopupContent.getMinimumHorizontalScrollPosition()) / 20;
					if (detailsPopupContent.getHorizontalScrollPosition() >
							detailsPopupContent.getMinimumHorizontalScrollPosition()) {
						detailsPopupContent.setHorizontalScrollPosition(
							detailsPopupContent.getHorizontalScrollPosition() - scrollIncrement);
					}
				}

				break;
/*
			case Event.ONCLICK:
				// XXX: Kind of hack-ish, but if the scrollpanel doesn't have focus
				// it won't allow scrolling with keys.
				focusContentPanel();
				break;
*/
		}
	}

}
