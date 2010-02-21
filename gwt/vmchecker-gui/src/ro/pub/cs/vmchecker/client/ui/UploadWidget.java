package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Widget;

public class UploadWidget extends Composite {

	private static UploadWidgetUiBinder uiBinder = GWT
			.create(UploadWidgetUiBinder.class);

	interface UploadWidgetUiBinder extends UiBinder<Widget, UploadWidget> {
	}

	@UiField 
	Button uploadButton; 
	
	@UiField
	FormPanel form; 
	
	public UploadWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		uploadButton.removeStyleName("gwt-Button");
		form.setEncoding(FormPanel.ENCODING_MULTIPART); 
		form.setMethod(FormPanel.METHOD_POST); 
	}
}
