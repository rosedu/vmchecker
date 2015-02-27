package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.dom.client.KeyUpHandler;
import com.google.gwt.event.dom.client.KeyUpEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ChangeEvent;
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
import com.google.gwt.user.client.ui.TreeItem;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.TakesValue;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;

import ro.pub.cs.vmchecker.client.presenter.UploadPresenter;
import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.i18n.UploadConstants;
import ro.pub.cs.vmchecker.client.ui.images.VmcheckerImages;

public class UploadWidget extends Composite
	implements UploadPresenter.UploadWidget, KeyUpHandler {

	private static UploadWidgetUiBinder uiBinder = GWT
			.create(UploadWidgetUiBinder.class);

	private static UploadConstants constants = GWT
		.create(UploadConstants.class);

	private static VmcheckerImages images = GWT
			.create(VmcheckerImages.class);

	interface UploadWidgetUiBinder extends UiBinder<Widget, UploadWidget> {
	}

	@UiField
	HTML uploadHeader;

	@UiField
	HTML uploadFooter;


	@UiField
	FormPanel md5Form;

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
	Hidden md5CourseIdField;

	@UiField
	Hidden md5AssignmentIdField;

	@UiField
	Button uploadMd5Button;


	@UiField
	FormPanel evaluationForm;

	@UiField
	Hidden evalCourseIdField;

	@UiField
	Hidden evalAssignmentIdField;

	@UiField
	Label fileListEmptyLabel;

	@UiField
	Button beginEvaluationButton;

	@UiField
	Tree fileListTree;

	@UiField
	Hidden evalArchiveFileNameField;

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


	@UiField
	FormPanel form;

	@UiField
	FileUpload fileUpload;

	@UiField
	Hidden courseIdField;

	@UiField
	Hidden assignmentIdField;

	@UiField
	Button uploadFileButton;



	public UploadWidget() {
		initWidget(uiBinder.createAndBindUi(this));

		md5Title.setText(constants.md5Title());
		md5SumOldDesc.setText(constants.md5SumOldDesc());
		md5SumTimeCommentLabel.setText(constants.md5SumTimeComment());
		md5SumDesc.setText(constants.md5SumDesc());
		md5SumEmptyLabel.setText(constants.md5SumEmpty());
		uploadMd5Button.setText(constants.uploadMd5Button());
		md5SumInputField.addKeyUpHandler(this);
		md5Form.setEncoding(FormPanel.ENCODING_MULTIPART);
		md5Form.setMethod(FormPanel.METHOD_POST);
		uploadMd5Button.removeStyleName("gwt-Button");

		archiveTitle.setText(constants.archiveTitle());
		archiveDesc.setText(constants.archiveDesc());
		fileListEmptyLabel.setText(constants.fileListEmpty());
		beginEvaluationButton.setText(constants.evaluationButton());
		evaluationForm.setEncoding(FormPanel.ENCODING_MULTIPART);
		evaluationForm.setMethod(FormPanel.METHOD_POST);
		beginEvaluationButton.removeStyleName("gwt-Button");
		listenFileListSelection();

		uploadFileButton.setText(constants.uploadFileButton());
		form.setEncoding(FormPanel.ENCODING_MULTIPART);
		form.setMethod(FormPanel.METHOD_POST);
		uploadFileButton.removeStyleName("gwt-Button");
	}

	@Override
	public FormPanel getUploadForm() {
		return form;
	}

	@Override
	public FormPanel getMd5UploadForm() {
		return md5Form;
	}

	@Override
	public TakesValue<String> getEvalArchiveFileNameField() {
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
	public HasClickHandlers getSubmitButton() {
		return uploadFileButton;
	}

	@Override
	public FormPanel getEvaluationForm() {
		return evaluationForm;
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

	@UiHandler("fileUpload")
	void handleChange(ChangeEvent event) {
		if (!fileUpload.getFilename().isEmpty()) {
			uploadFileButton.setEnabled(true);
		}
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

	@Override
	public void setUploadType(Assignment.StorageType type) {
		if (type == Assignment.StorageType.NORMAL) {
			uploadHeader.setHTML(constants.uploadNormalHeader());
			uploadFooter.setHTML(constants.uploadNormalFooter());
			md5Form.setVisible(false);
			evaluationForm.setVisible(false);
			form.setVisible(true);
		} else {
			uploadHeader.setHTML(constants.uploadLargeHeader());
			uploadFooter.setHTML(constants.uploadLargeFooter());
			md5Form.setVisible(false);
			evaluationForm.setVisible(false);
			form.setVisible(true);
		}

	}

	@Override
	public void setParameters(String courseId, String assignmentId) {
		md5CourseIdField.setValue(courseId);
		md5AssignmentIdField.setValue(assignmentId);
		evalCourseIdField.setValue(courseId);
		evalAssignmentIdField.setValue(assignmentId);
		courseIdField.setValue(courseId);
		assignmentIdField.setValue(assignmentId);
	}

	@Override
	public void populateFileList(Assignment assignment, String[] files) {

		/* Define the image strings */
		String folderImage = AbstractImagePrototype.create(images.folder()).getHTML();
		String zipImage = AbstractImagePrototype.create(images.zip()).getHTML();
		String fileImage = AbstractImagePrototype.create(images.file()).getHTML();

		Tree tree = fileListTree;
		TreeItem treeRoot;
		String firstFile = files[0].substring((assignment.storageBasepath + "/").length());
		String userDir = firstFile.substring(0, firstFile.indexOf('/'));
		tree.removeItems();
		treeRoot = tree.addTextItem(AbstractImagePrototype.create(images.connection()).getHTML() + " " + userDir + "@" + assignment.storageHost);

		for(String s : files) {
			String file = s.substring((assignment.storageBasepath + "/").length());
			file = file.substring(file.indexOf('/') + 1);
			TreeItem treeBranch = treeRoot;

			while(file.indexOf('/') != -1) {
				String folderPart = file.substring(0, file.indexOf('/'));
				file = file.substring(file.indexOf('/') + 1);

				int existingFolders;
				boolean found = false;
				existingFolders = treeBranch.getChildCount();
				for(int i = 0 ; i < existingFolders ; i++) {
					String branchText = treeBranch.getChild(i).getText();
					branchText = branchText.substring(branchText.indexOf('>') + 2);
					if(branchText.equals(folderPart)) {
						treeBranch = treeBranch.getChild(i);
						found = true;
						break;
					}
				}

				if(!found) treeBranch = treeBranch.addTextItem(folderImage + " " +  folderPart);
			}

			String fileName = file.trim(); /* Eliminate all trailing end-of-line characters */
			if(fileName.indexOf('.') != -1)
				if(fileName.substring(fileName.indexOf('.') + 1).equals("zip"))
					treeBranch.addTextItem(zipImage + " " + fileName);
				else
					treeBranch.addTextItem(fileImage + " " + fileName);
			else
				treeBranch.addTextItem(fileImage + " " + fileName);
		}

		fileListTree.setAnimationEnabled(true);
	}

	private void listenFileListSelection() {

		fileListTree.addSelectionHandler(new SelectionHandler<TreeItem> () {

			public void onSelection(SelectionEvent<TreeItem> event) {
				TreeItem item = event.getSelectedItem();

				if(item.getChildCount() != 0)
					beginEvaluationButton.setEnabled(false);
				else {
					beginEvaluationButton.setEnabled(true);

					TreeItem temp_item = item;
					String selectedArchiveFileName = item.getText();
					/* Eliminate the <img /> tag before the folder name */
					selectedArchiveFileName = selectedArchiveFileName.substring(selectedArchiveFileName.indexOf('>') + 2);

					while(temp_item.getParentItem() != null) {

						temp_item = temp_item.getParentItem();
						if(temp_item.getParentItem() == null) break;
						String folderName = temp_item.getText();
						/* Eliminate the <img /> tag before the folder name */
						folderName = folderName.substring(folderName.indexOf('>') + 2);
						selectedArchiveFileName = folderName + "/" + selectedArchiveFileName;
					}

					evalArchiveFileNameField.setValue(selectedArchiveFileName);
				}
			}});
	}

}
