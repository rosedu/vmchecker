package ro.pub.cs.vmchecker.client.ui;

import java.util.ArrayList;

import com.google.gwt.user.client.ui.SimplePanel;
import com.google.gwt.user.client.ui.Widget;

public class ViewStack extends SimplePanel {
	
	private ArrayList<Widget> views = new ArrayList<Widget>();
	
	/**
	 * a selectedIndex of value -1 means there is no active view 
	 */
	private int selectedIndex = -1; 
	
	
	public void addView(Widget view) {
		views.add(view); 
	}
	
	public void removeView(Widget view) {
		int index = views.indexOf(view); 
		if (index != -1 && index == selectedIndex) {
			remove(view); 
			selectedIndex = -1; 
		} else if (index < selectedIndex) {
			selectedIndex--; 
		}
		views.remove(view); 
	}
	
	public void setSelectedIndex(int selectedIndex) {
		if ((selectedIndex < -1) || (selectedIndex >= views.size()))
			throw new IndexOutOfBoundsException(); 
		
		if (selectedIndex != this.selectedIndex) {
			/* if there is an active view, pop it */
			if (this.selectedIndex != -1) {
				this.clear(); 
			}
			/* if the index is an actual value */
			if (selectedIndex != -1) {
				this.add(views.get(selectedIndex)); 
			}
			this.selectedIndex = selectedIndex; 
		}
	}
	
	public int getSelectedIndex() {
		return selectedIndex; 
	}
}
