package ro.pub.cs.vmchecker.client.presenter;

import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.user.client.ui.HasWidgets;

public class MenuPresenter implements Presenter {

	public interface Widget extends HasClickHandlers {
		public void setSelectedIndex(int selectedIndex); 
		public int getSelectedIndex(); 
	}

	private EventBus eventBus;
	private MenuPresenter.Widget widget; 
	
	public MenuPresenter(EventBus eventBus, MenuPresenter.Widget widget) {
		this.eventBus = eventBus;
		bindWidget(widget); 
	}
	
	private void bindWidget(MenuPresenter.Widget widget) {
		this.widget = widget; 
	}
	
	public MenuPresenter.Widget getWidget() {
		return widget; 
	}
	
	@Override
	public void go(HasWidgets container) {
		container.add((com.google.gwt.user.client.ui.Widget)widget); 
	}

	@Override
	public void clearEventHandlers() {
		/* nothing to clear */
	}

}
