package ro.pub.cs.vmchecker.client.ui;

import java.util.ArrayList;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import ro.pub.cs.vmchecker.client.presenter.MenuPresenter;

public class NumberedMenu extends Composite 
	implements ClickHandler, MenuPresenter.Widget {

	private static NumberedMenuUiBinder uiBinder = GWT
			.create(NumberedMenuUiBinder.class);

	interface NumberedMenuUiBinder extends UiBinder<Widget, NumberedMenu> {
	}

	private ArrayList<NumberedMenuItem> items; 
	private int selectedIndex = -1; 
	
	@UiField
	VerticalPanel panel; 

	public NumberedMenu(String[] itemsText) {
		initWidget(uiBinder.createAndBindUi(this));
		items = new ArrayList<NumberedMenuItem>(); 
		for (int i = 0; i < itemsText.length; i++) {
			NumberedMenuItem item = new NumberedMenuItem(i + 1, itemsText[i], Integer.toString(i));
			item.addClickHandler(this); 
			panel.add(item);
			items.add(item); 
		}
		/* initialize */
		setSelectedIndex(0); 
	}

	@Override
	public void onClick(ClickEvent event) {
		int i = items.indexOf(event.getSource());
		if ((i >= 0) && (i != selectedIndex)) {
			setSelectedIndex(i); 
		} else if (i == selectedIndex) {
			event.stopPropagation(); 
		}
	}
	
	@Override
	public void setSelectedIndex(int selectedIndex) {
		if (this.selectedIndex != selectedIndex) {
			if (this.selectedIndex >= 0) {
				items.get(this.selectedIndex).setSelected(false);
			}
			if (selectedIndex >= 0) {
				items.get(selectedIndex).setSelected(true);				
			}
			this.selectedIndex = selectedIndex;
		}
	}
	
	@Override
	public int getSelectedIndex() {
		return selectedIndex; 
	}

	@Override
	public HandlerRegistration addClickHandler(ClickHandler handler) {
		return addDomHandler(handler, ClickEvent.getType());
	}
	
}
