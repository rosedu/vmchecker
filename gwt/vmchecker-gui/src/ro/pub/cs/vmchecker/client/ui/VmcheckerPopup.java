package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.SimplePanel;

/**
 * Wrapper over the classic PopupPanel
 * Adds a close button and a scrollable content panel 
 * @author claudiugh
 *
 */
public class VmcheckerPopup extends PopupPanel {

	private static final String containerStyle = "popupContainer"; 
	private static final String contentStyle = "popupContentPanel"; 
	
	private FlowPanel detailsPopupContainer = new FlowPanel(); 
	private SimplePanel detailsPopupContent = new SimplePanel(); 
	private Anchor popupCloseButton = new Anchor("close");
	
	public VmcheckerPopup() {
		super(true, true);
		setup(); 
	}
	
	private void setup() {
		hide();
		setWidth("" + (Window.getClientWidth()/2) + "px"); 
		setHeight("" + (Window.getClientHeight() - 200) + "px");
		setGlassEnabled(true);
		detailsPopupContainer.add(popupCloseButton);
		detailsPopupContainer.add(detailsPopupContent);
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
	}
	
}
