package ro.pub.cs.vmchecker.client.presenter;

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
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HasHTML;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.TakesValue;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.FormPanel.SubmitEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;

public class UploadPresenter implements Presenter, SubmitCompleteHandler {

	public interface UploadWidget {
		HasClickHandlers getMd5SubmitButton();
		HasClickHandlers getBeginEvaluationButton();
		HasText getFileListEmptyLabel();
		FormPanel getMd5UploadForm();
		FormPanel getEvaluationForm();
		TakesValue<String> getEvalArchiveFileNameField();
		void setFileListEmptyLabelVisible(boolean visible);
		void setBeginEvaluationButtonEnabled(boolean enabled);
		void resetMd5SumInfo();
		void displayMd5SumInfo(String md5Sum, String uploadTime);
		boolean validateMd5Sum(boolean onSubmit);
		HasClickHandlers getSubmitButton();
		FormPanel getUploadForm();
		void setUploadType(Assignment.StorageType type);
		void updateWidget(String courseId, Assignment assignment);
		void populateFileList(String[] files);
	}

	private EventBus eventBus;
	private HTTPService service;
	private String courseId;
	private Assignment assignment;
	private String selectedArchiveFileName;
	private HasWidgets container;

	private UploadWidget uploadWidget = new ro.pub.cs.vmchecker.client.ui.UploadWidget();

	private static VmcheckerConstants constants = GWT
			.create(VmcheckerConstants.class);

	public UploadPresenter(EventBus eventBus, HTTPService service) {
		this.eventBus = eventBus;
		this.service = service;
		listenSubmitUpload();
		listenMd5SubmitUpload();

		uploadWidget.getUploadForm().setAction(HTTPService.UPLOAD_URL);
		uploadWidget.getUploadForm().addSubmitCompleteHandler(this);
		uploadWidget.getMd5UploadForm().setAction(HTTPService.UPLOAD_MD5_URL);
		uploadWidget.getMd5UploadForm().addSubmitCompleteHandler(this);
		uploadWidget.getEvaluationForm().setAction(HTTPService.BEGIN_EVALUATION_URL);
		uploadWidget.getEvaluationForm().addSubmitCompleteHandler(this);
	}

	@Override
	public void onSubmitComplete(SubmitCompleteEvent event) {

		/*
		 * Yes, I know there is a lot repetetive code here. It's not pretty but until
		 * further notice it gets the job done. If ever in the future the form handling
		 * will be moved to a more generic implementation this should probably be
		 * changed.
		 */

		if (event.getSource() == uploadWidget.getUploadForm()) {

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

		if (event.getSource() == uploadWidget.getMd5UploadForm()) {

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

		if (event.getSource() == uploadWidget.getEvaluationForm()) {

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
				GWT.log("[UploadPresenter]", caught);
				eventBus.fireEvent(new ErrorDisplayEvent(constants.loadMd5sumFail(), caught.getMessage()));
			}

			public void onSuccess(Md5Status md5Status) {
				if(md5Status.fileExists) {
					uploadWidget.displayMd5SumInfo(md5Status.md5Sum, md5Status.uploadTime);
					eventBus.fireEvent(new StatusChangedEvent(
						StatusChangedEvent.StatusType.RESET, ""));
					loadFileList();
					listenBeginEvaluation();
					uploadWidget.setFileListEmptyLabelVisible(false);
					uploadWidget.getEvaluationForm().setVisible(true);
				} else {
					uploadWidget.getEvaluationForm().setVisible(false);
					eventBus.fireEvent(new StatusChangedEvent(
						StatusChangedEvent.StatusType.RESET, ""));
				}
			}
		});
	}

	public void loadAndDisplayUpload() {

		uploadWidget.setUploadType(assignment.storageType);
		if (assignment.storageType == Assignment.StorageType.LARGE) {
			uploadWidget.resetMd5SumInfo();
			loadAndDisplayMd5Sum();
		}
		displayView((com.google.gwt.user.client.ui.Widget)uploadWidget);
	}

	private void loadFileList() {

		eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION,
			constants.loadStorageDir()));

		service.getStorageDirContents(courseId, assignment.id, new AsyncCallback<FileList>() {

			public void onFailure(Throwable caught) {
				GWT.log("[UploadPresenter]", caught);
				eventBus.fireEvent(new ErrorDisplayEvent(constants.loadStorageDirFail(), caught.getMessage()));
			}

			public void onSuccess(FileList fileList) {
				uploadWidget.setFileListEmptyLabelVisible(true);
				if(fileList.Files != null) {
					uploadWidget.populateFileList(fileList.Files);
					uploadWidget.setFileListEmptyLabelVisible(false);
				} else
					uploadWidget.setFileListEmptyLabelVisible(true);
				eventBus.fireEvent(new StatusChangedEvent(
						StatusChangedEvent.StatusType.RESET, ""));
			}
		});

	}

	private void listenSubmitUpload() {
		uploadWidget.getSubmitButton().addClickHandler(new ClickHandler() {

			public void onClick(ClickEvent event) {
				eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION, constants.uploadFile()));
				uploadWidget.getUploadForm().submit();
			}
		});
	}

	private void listenMd5SubmitUpload() {
		uploadWidget.getMd5SubmitButton().addClickHandler(new ClickHandler() {

			public void onClick(ClickEvent event) {
				if(uploadWidget.validateMd5Sum(true)) {
					eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION, constants.uploadMd5()));
					uploadWidget.getMd5UploadForm().submit();
				}
			}
		});
	}

	private void listenBeginEvaluation() {

		uploadWidget.getBeginEvaluationButton().addClickHandler(new ClickHandler() {

			public void onClick(ClickEvent event) {
				eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION, constants.evaluate()));
				uploadWidget.getEvaluationForm().submit();
			}
		});

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
		uploadWidget.updateWidget(courseId, assignment);
	}

	public void displayView(com.google.gwt.user.client.ui.Widget widget) {
		container.clear();
		container.add(widget);
	}

}
