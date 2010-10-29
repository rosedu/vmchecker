package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.HTML;

import ro.pub.cs.vmchecker.client.presenter.AssignmentBoardUploadPresenter;
import ro.pub.cs.vmchecker.client.i18n.UploadConstants;

public class UploadNormalWidget extends Composite
	implements AssignmentBoardUploadPresenter.UploadNormalWidget {

	private static UploadNormalWidgetUiBinder uiBinder = GWT
			.create(UploadNormalWidgetUiBinder.class);

	private static UploadConstants constants = GWT
			.create(UploadConstants.class);

	interface UploadNormalWidgetUiBinder extends UiBinder<Widget, UploadNormalWidget> {
	}

	@UiField
	Button uploadFileButton;

	@UiField
	FormPanel form;

	@UiField
	Hidden courseIdField;

	@UiField
	Hidden assignmentIdField;

	@UiField
	FileUpload fileUpload;

	@UiField
	HTML uploadNormalHeader;

	@UiField
	HTML uploadNormalFooter;

	public UploadNormalWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		uploadFileButton.setText(constants.uploadFileButton());
		uploadNormalHeader.setHTML(constants.uploadNormalHeader());
		uploadNormalFooter.setHTML(constants.uploadNormalFooter());
		uploadFileButton.removeStyleName("gwt-Button");
		form.setEncoding(FormPanel.ENCODING_MULTIPART);
		form.setMethod(FormPanel.METHOD_POST);
	}

	@UiHandler("fileUpload")
	void handleChange(ChangeEvent event) {
		if (!fileUpload.getFilename().isEmpty()) {
			uploadFileButton.setEnabled(true);
		}
	}

	@Override
	public FormPanel getUploadForm() {
		return form;
	}

	@Override
	public Hidden getAssignmentField() {
		return assignmentIdField;
	}

	@Override
	public Hidden getCourseField() {
		return courseIdField;
	}

	@Override
	public HasClickHandlers getSubmitButton() {
		return uploadFileButton;
	}

}
