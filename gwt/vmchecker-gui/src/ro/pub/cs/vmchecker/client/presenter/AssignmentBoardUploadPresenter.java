package ro.pub.cs.vmchecker.client.presenter;

import ro.pub.cs.vmchecker.client.ui.images.VmcheckerImages;
import ro.pub.cs.vmchecker.client.i18n.VmcheckerConstants;
import ro.pub.cs.vmchecker.client.event.ErrorDisplayEvent;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent;
import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.model.EvaluationResult;
import ro.pub.cs.vmchecker.client.model.LargeEvaluationResponse;
import ro.pub.cs.vmchecker.client.model.UploadStatus;
import ro.pub.cs.vmchecker.client.model.Md5Status;
import ro.pub.cs.vmchecker.client.model.FileList;
import ro.pub.cs.vmchecker.client.service.HTTPService;
import ro.pub.cs.vmchecker.client.service.ServiceError;
import ro.pub.cs.vmchecker.client.service.json.UploadResponseDecoder;
import ro.pub.cs.vmchecker.client.service.json.LargeEvaluationResponseDecoder;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.KeyUpEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyUpHandler;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.dom.client.HasKeyPressHandlers;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HasHTML;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Tree;
import com.google.gwt.user.client.ui.TreeItem;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.FormPanel.SubmitEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;

public class AssignmentBoardUploadPresenter implements Presenter, SubmitCompleteHandler {

	public interface UploadNormalWidget {
		HasClickHandlers getSubmitButton();
		FormPanel getUploadForm();
		Hidden getCourseField();
		Hidden getAssignmentField();
	}

	public interface UploadLargeWidget {
		HasClickHandlers getMd5SubmitButton();
		HasClickHandlers getBeginEvaluationButton();
		HasText getFileListEmptyLabel();
		FormPanel getMd5UploadForm();
		FormPanel getEvaluationForm();
		Hidden getCourseField();
		Hidden getAssignmentField();
		Hidden getEvalCourseField();
		Hidden getEvalAssignmentField();
		Hidden getEvalArchiveFileNameField();
		void setFileListEmptyLabelVisible(boolean visible);
		void setBeginEvaluationButtonEnabled(boolean enabled);
		void resetMd5SumInfo();
		void displayMd5SumInfo(String md5Sum, String uploadTime);
		boolean validateMd5Sum(boolean onSubmit);
		Tree getFileListTree();
	}

	private HandlerManager eventBus;
	private HTTPService service;
	private String courseId;
	private Assignment assignment;
	private String selectedArchiveFileName;
	private HasWidgets container;

	private UploadNormalWidget uploadNormalWidget = new ro.pub.cs.vmchecker.client.ui.UploadNormalWidget();
	private UploadLargeWidget uploadLargeWidget = new ro.pub.cs.vmchecker.client.ui.UploadLargeWidget();

	private static VmcheckerConstants constants = GWT
			.create(VmcheckerConstants.class);
	private static VmcheckerImages images = GWT
			.create(VmcheckerImages.class);


	public AssignmentBoardUploadPresenter(HandlerManager eventBus, HTTPService service) {
		this.eventBus = eventBus;
		this.service = service;
		listenSubmitUpload();
		listenMd5SubmitUpload();

		uploadNormalWidget.getUploadForm().setAction(HTTPService.UPLOAD_URL);
		uploadNormalWidget.getUploadForm().addSubmitCompleteHandler(this);
		uploadLargeWidget.getMd5UploadForm().setAction(HTTPService.UPLOAD_MD5_URL);
		uploadLargeWidget.getMd5UploadForm().addSubmitCompleteHandler(this);
		uploadLargeWidget.getEvaluationForm().setAction(HTTPService.BEGIN_EVALUATION_URL);
		uploadLargeWidget.getEvaluationForm().addSubmitCompleteHandler(this);
	}

	@Override
	public void onSubmitComplete(SubmitCompleteEvent event) {

		/*
		 * Yes, I know there is a lot repetetive code here. It's not pretty but until
		 * further notice it gets the job done. If ever in the future the form handling
		 * will be moved to a more generic implementation this should probably be
		 * changed.
		 */

		if (event.getSource() == uploadNormalWidget.getUploadForm()) {

			/* Normal assignment file submission response */

			UploadResponseDecoder responseDecoder = new UploadResponseDecoder();
			responseDecoder.parse(event.getResults());
			if (!responseDecoder.errorsEncountered()) {
				UploadStatus response = responseDecoder.getResult();
				StatusChangedEvent statusChangeEvent = null;
				if (response.status) {
					statusChangeEvent = new StatusChangedEvent(StatusChangedEvent.StatusType.SUCCESS,
								constants.uploadFileSuccess());
				} else {
					statusChangeEvent = new StatusChangedEvent(StatusChangedEvent.StatusType.ERROR,
								constants.uploadFileFail());
				}
				eventBus.fireEvent(statusChangeEvent);
			} else {
				ServiceError se = new ServiceError(eventBus, HTTPService.UPLOAD_URL);
				se.parseError(event.getResults());
			}
		}

		if (event.getSource() == uploadLargeWidget.getMd5UploadForm()) {

			/* Large assignment md5 submission response */

			UploadResponseDecoder responseDecoder = new UploadResponseDecoder();
			responseDecoder.parse(event.getResults());
			if (!responseDecoder.errorsEncountered()) {
				UploadStatus response = responseDecoder.getResult();
				StatusChangedEvent statusChangeEvent = null;
				if (response.status) {
					statusChangeEvent = new StatusChangedEvent(StatusChangedEvent.StatusType.SUCCESS,
								constants.uploadMd5Success());
				} else {
					statusChangeEvent = new StatusChangedEvent(StatusChangedEvent.StatusType.ERROR,
								constants.uploadMd5Fail());
				}
				loadAndDisplayUpload();
				eventBus.fireEvent(statusChangeEvent);
			} else {
				ServiceError se = new ServiceError(eventBus, HTTPService.UPLOAD_MD5_URL);
				se.parseError(event.getResults());
			}

		}

		if (event.getSource() == uploadLargeWidget.getEvaluationForm()) {

			/* Large assignment evaluation request response */

			LargeEvaluationResponseDecoder responseDecoder = new LargeEvaluationResponseDecoder();
			responseDecoder.parse(event.getResults());
			if (!responseDecoder.errorsEncountered()) {
				LargeEvaluationResponse response = responseDecoder.getResult();
				StatusChangedEvent statusChangeEvent = null;
				if (response.status) {
					statusChangeEvent = new StatusChangedEvent(StatusChangedEvent.StatusType.SUCCESS,
								constants.evaluateSuccess());
				} else {
					statusChangeEvent = new StatusChangedEvent(StatusChangedEvent.StatusType.ERROR,
						response.error);
					if (response.error.equals("md5"))
						statusChangeEvent = new StatusChangedEvent(StatusChangedEvent.StatusType.ERROR,
							constants.evaluateFailMd5());
					if (response.error.equals("zip"))
						statusChangeEvent = new StatusChangedEvent(StatusChangedEvent.StatusType.ERROR,
							constants.evaluateFailZip());
				}
				eventBus.fireEvent(statusChangeEvent);
			} else {
				ServiceError se = new ServiceError(eventBus, HTTPService.BEGIN_EVALUATION_URL);
				se.parseError(event.getResults());
			}
		}

	}

	private void loadAndDisplayMd5Sum() {

		eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION,
				constants.loadMd5sum()));

		service.getUploadedMd5(courseId, assignment.id, new AsyncCallback<Md5Status>() {

			public void onFailure(Throwable caught) {
				GWT.log("[AssignmentBoardUploadPresenter]", caught);
				eventBus.fireEvent(new ErrorDisplayEvent(constants.loadMd5sumFail(), caught.getMessage()));
			}

			public void onSuccess(Md5Status md5Status) {
				if(md5Status.fileExists) {
					uploadLargeWidget.displayMd5SumInfo(md5Status.md5Sum, md5Status.uploadTime);
					eventBus.fireEvent(new StatusChangedEvent(
						StatusChangedEvent.StatusType.RESET, ""));
					loadFileList();
					listenFileListSelection();
					listenBeginEvaluation();
					uploadLargeWidget.setFileListEmptyLabelVisible(false);
					uploadLargeWidget.getEvaluationForm().setVisible(true);
				} else {
					uploadLargeWidget.getEvaluationForm().setVisible(false);
					eventBus.fireEvent(new StatusChangedEvent(
						StatusChangedEvent.StatusType.RESET, ""));
				}
				displayView((com.google.gwt.user.client.ui.Widget)uploadLargeWidget);
			}
		});
	}

	public void loadAndDisplayUpload() {

		if(assignment.storageType.equals("normal")) {
			displayView((com.google.gwt.user.client.ui.Widget)uploadNormalWidget);
		} else {
			uploadLargeWidget.resetMd5SumInfo();
			loadAndDisplayMd5Sum();
		}
	}

	private void loadFileList() {

		eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION,
			constants.loadStorageDir()));

		service.getStorageDirContents(courseId, assignment.id, new AsyncCallback<FileList>() {

			public void onFailure(Throwable caught) {
				GWT.log("[AssignmentBoardUploadPresenter]", caught);
				eventBus.fireEvent(new ErrorDisplayEvent(constants.loadStorageDirFail(), caught.getMessage()));
			}

			public void onSuccess(FileList fileList) {
				uploadLargeWidget.setFileListEmptyLabelVisible(true);
				if(fileList.Files != null) {
					populateFileListTree(fileList.Files);
					uploadLargeWidget.getFileListTree().setAnimationEnabled(true);
					uploadLargeWidget.setFileListEmptyLabelVisible(false);
				} else
					uploadLargeWidget.setFileListEmptyLabelVisible(true);
				eventBus.fireEvent(new StatusChangedEvent(
						StatusChangedEvent.StatusType.RESET, ""));
			}
		});

	}

	private void listenSubmitUpload() {
		uploadNormalWidget.getSubmitButton().addClickHandler(new ClickHandler() {

			public void onClick(ClickEvent event) {
				uploadNormalWidget.getCourseField().setValue(courseId);
				uploadNormalWidget.getAssignmentField().setValue(assignment.id);
				eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION, constants.uploadFile()));
				uploadNormalWidget.getUploadForm().submit();
			}
		});
	}

	private void listenMd5SubmitUpload() {
		uploadLargeWidget.getMd5SubmitButton().addClickHandler(new ClickHandler() {

			public void onClick(ClickEvent event) {
				if(uploadLargeWidget.validateMd5Sum(true)) {
					uploadLargeWidget.getCourseField().setValue(courseId);
					uploadLargeWidget.getAssignmentField().setValue(assignment.id);
					eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION, constants.uploadMd5()));
					uploadLargeWidget.getMd5UploadForm().submit();
				}
			}
		});
	}

	private void listenBeginEvaluation() {

		uploadLargeWidget.getBeginEvaluationButton().addClickHandler(new ClickHandler() {

			public void onClick(ClickEvent event) {
				eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION, constants.evaluate()));
				uploadLargeWidget.getEvalCourseField().setValue(courseId);
				uploadLargeWidget.getEvalAssignmentField().setValue(assignment.id);
				uploadLargeWidget.getEvalArchiveFileNameField().setValue(AssignmentBoardUploadPresenter.this.selectedArchiveFileName);
				uploadLargeWidget.getEvaluationForm().submit();
			}
		});

	}

	private void listenFileListSelection() {

		uploadLargeWidget.getFileListTree().addSelectionHandler(new SelectionHandler<TreeItem> () {

			public void onSelection(SelectionEvent<TreeItem> event) {
				TreeItem item = event.getSelectedItem();

				if(item.getChildCount() != 0)
					uploadLargeWidget.setBeginEvaluationButtonEnabled(false);
				else {
					uploadLargeWidget.setBeginEvaluationButtonEnabled(true);

					TreeItem temp_item = item;
					selectedArchiveFileName = item.getText();
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
				}

			}});
	}

	private void populateFileListTree(String[] files) {

		/* Define the image strings */
		String folderImage = AbstractImagePrototype.create(images.folder()).getHTML();
		String zipImage = AbstractImagePrototype.create(images.zip()).getHTML();
		String fileImage = AbstractImagePrototype.create(images.file()).getHTML();

		Tree tree = uploadLargeWidget.getFileListTree();
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
	}

	@Override
	public void go(HasWidgets container) {
		this.container = container;
	}

	@Override
	public void clearEventHandlers() {
	}

	public void setParameters(String courseId, Assignment assignment) {
		this.courseId = courseId;
		this.assignment = assignment;
	}

	public void displayView(com.google.gwt.user.client.ui.Widget widget) {
		container.clear();
		container.add(widget);
	}

}
