package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.dom.client.KeyUpHandler;
import com.google.gwt.event.dom.client.KeyUpEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.HasKeyPressHandlers;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Tree;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HTML;

import ro.pub.cs.vmchecker.client.presenter.AssignmentBoardUploadPresenter;
import ro.pub.cs.vmchecker.client.i18n.UploadConstants;

public class UploadLargeWidget extends Composite
	implements AssignmentBoardUploadPresenter.UploadLargeWidget, KeyUpHandler {

	private static UploadLargeWidgetUiBinder uiBinder = GWT
			.create(UploadLargeWidgetUiBinder.class);

	private static UploadConstants constants = GWT
		.create(UploadConstants.class);

	interface UploadLargeWidgetUiBinder extends UiBinder<Widget, UploadLargeWidget> {
	}

	@UiField
	Button uploadMd5Button;

	@UiField
	FormPanel md5Form;

	@UiField
	FormPanel evaluationForm;

	@UiField
	Hidden courseIdField;

	@UiField
	Hidden assignmentIdField;

	@UiField
	TextBox md5SumInputField;

	@UiField
	Label md5SumValueLabel;

	@UiField
	Label md5SumEmptyLabel;

	@UiField
	Label md5SumTimeLabel;

	@UiField
	Label md5SumTimeCommentLabel;

	@UiField
	Label md5SumInputCommentLabel;

	@UiField
	Label fileListEmptyLabel;

	@UiField
	Button beginEvaluationButton;

	@UiField
	Tree fileListTree;

	@UiField
	Hidden evalCourseIdField;

	@UiField
	Hidden evalAssignmentIdField;

	@UiField
	Hidden evalArchiveFileNameField;

	@UiField
	HTML uploadLargeHeader;

	@UiField
	HTML uploadLargeFooter;

	@UiField
	Label md5Title;

	@UiField
	Label md5SumOldDesc;

	@UiField
	Label md5SumDesc;

	@UiField
	Label archiveTitle;

	@UiField
	Label archiveDesc;

	public UploadLargeWidget() {
		initWidget(uiBinder.createAndBindUi(this));

		uploadLargeHeader.setHTML(constants.uploadLargeHeader());
		uploadLargeFooter.setHTML(constants.uploadLargeFooter());
		md5Title.setText(constants.md5Title());
		md5SumOldDesc.setText(constants.md5SumOldDesc());
		md5SumTimeCommentLabel.setText(constants.md5SumTimeComment());
		md5SumDesc.setText(constants.md5SumDesc());
		md5SumEmptyLabel.setText(constants.md5SumEmpty());
		uploadMd5Button.setText(constants.uploadMd5Button());
		archiveTitle.setText(constants.archiveTitle());
		archiveDesc.setText(constants.archiveDesc());
		fileListEmptyLabel.setText(constants.fileListEmpty());
		beginEvaluationButton.setText(constants.evaluationButton());

		md5SumInputField.addKeyUpHandler(this);
		md5Form.setEncoding(FormPanel.ENCODING_MULTIPART);
		md5Form.setMethod(FormPanel.METHOD_POST);
		evaluationForm.setEncoding(FormPanel.ENCODING_MULTIPART);
		evaluationForm.setMethod(FormPanel.METHOD_POST);

	}

	@Override
	public FormPanel getMd5UploadForm() {
		return md5Form;
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
	public Hidden getEvalAssignmentField() {
		return evalAssignmentIdField;
	}

	@Override
	public Hidden getEvalCourseField() {
		return evalCourseIdField;
	}

	@Override
	public Hidden getEvalArchiveFileNameField() {
		return evalArchiveFileNameField;
	}

	@Override
	public HasClickHandlers getMd5SubmitButton() {
		return uploadMd5Button;
	}

	@Override
	public HasClickHandlers getBeginEvaluationButton() {
		return beginEvaluationButton;
	}

	@Override
	public FormPanel getEvaluationForm() {
		return evaluationForm;
	}

	@Override
	public Tree getFileListTree() {
		return fileListTree;
	}

	@Override
	public HasText getFileListEmptyLabel() {
		return fileListEmptyLabel;
	}

	@Override
	public void setFileListEmptyLabelVisible(boolean visible) {
		fileListEmptyLabel.setVisible(visible);
	}

	@Override
	public void setBeginEvaluationButtonEnabled(boolean enabled) {
		beginEvaluationButton.setEnabled(enabled);
	}

	public void onKeyUp(KeyUpEvent event) {
		validateMd5Sum(false);
	}


	@Override
	public boolean validateMd5Sum(boolean onSubmit) {

		String md5 = md5SumInputField.getText().trim().toLowerCase();

		for(int i = 0 ; i < md5.length() ; i++)
			if(Character.digit(md5.charAt(i), 16) == -1) {
				md5SumInputCommentLabel.setText(constants.md5sumInvalid());
				md5SumInputCommentLabel.setVisible(true);
				return false;
			}

		md5SumInputCommentLabel.setVisible(false);

		if(md5.length() == 32 || (md5.length() == 0 && !onSubmit)) return true;
		else {
			md5SumInputCommentLabel.setText(constants.md5sumIncomplete());
			md5SumInputCommentLabel.setVisible(true);
			return false;
		}
	}

	@Override
	public void displayMd5SumInfo(String md5Sum, String uploadTime) {

		md5SumEmptyLabel.setVisible(false);
		md5SumValueLabel.setVisible(true);
		md5SumValueLabel.setText(md5Sum);
		md5SumTimeLabel.setText(uploadTime);
		md5SumTimeCommentLabel.setVisible(true);
		md5SumTimeLabel.setVisible(true);

	}

	@Override
	public void resetMd5SumInfo() {

		md5Form.reset();
		md5SumInputCommentLabel.setVisible(false);
		md5SumEmptyLabel.setVisible(true);
		md5SumValueLabel.setText("");
		md5SumValueLabel.setVisible(false);
		md5SumTimeCommentLabel.setVisible(false);
		md5SumTimeLabel.setVisible(false);

	}



}
