package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Widget;

import ro.pub.cs.vmchecker.client.presenter.AssignmentBoardPresenter;

public class UploadWidget extends Composite 
	implements AssignmentBoardPresenter.UploadWidget {

	private static UploadWidgetUiBinder uiBinder = GWT
			.create(UploadWidgetUiBinder.class);

	interface UploadWidgetUiBinder extends UiBinder<Widget, UploadWidget> {
	}

	@UiField 
	Button uploadButton; 
	
	@UiField
	FormPanel form; 
	
	@UiField
	Hidden courseIdField; 
	
	@UiField
	Hidden assignmentIdField; 
	
	@UiField 
	FileUpload fileUpload; 
	
	public UploadWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		uploadButton.removeStyleName("gwt-Button");
		form.setEncoding(FormPanel.ENCODING_MULTIPART); 
		form.setMethod(FormPanel.METHOD_POST); 
	}

	@UiHandler("fileUpload")
	void handleChange(ChangeEvent event) {
		if (!fileUpload.getFilename().isEmpty()) {
			uploadButton.setEnabled(true); 
		}
	}
	
	@Override
	public FormPanel getUploadForm() {
		return form; 
	}

	@Override
	public Hidden getAssignmentField() {
		return courseIdField; 
	}

	@Override
	public Hidden getCourseField() {
		return assignmentIdField; 
	}

	@Override
	public HasClickHandlers getSubmitButton() {
		return uploadButton; 
	}

}
