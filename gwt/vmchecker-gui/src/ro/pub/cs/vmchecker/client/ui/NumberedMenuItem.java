package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.resources.client.CssResource;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class NumberedMenuItem extends Composite 
	implements HasClickHandlers {

	private static NumberedMenuItemUiBinder uiBinder = GWT
			.create(NumberedMenuItemUiBinder.class);

	interface NumberedMenuItemUiBinder extends
			UiBinder<Widget, NumberedMenuItem> {
	}

	interface ItemStyle extends CssResource {
		String selected();
		String unselected();
	}
	
	private String value; 
	
	@UiField 
	Label itemNo; 
	
	@UiField
	Anchor itemAnchor;

	@UiField 
	ItemStyle style;
	
	public NumberedMenuItem(int no, String text, String value) {
		initWidget(uiBinder.createAndBindUi(this));
		this.value = value;
		itemNo.setText(Integer.toString(no) + "."); 
		itemAnchor.setText(text); 
		itemAnchor.setTitle(text); 
	}

	@UiHandler("itemAnchor")
	void onClick(ClickEvent event) {
		/* default is propagated to the upper layers */
	}

	@Override
	public HandlerRegistration addClickHandler(ClickHandler handler) {
		return addDomHandler(handler, ClickEvent.getType());
	}

	public void setSelected(boolean selected) {
		this.addStyleName(selected ? style.selected() : style.unselected()); 
		this.removeStyleName(selected ? style.unselected() : style.selected()); 
	}
}
